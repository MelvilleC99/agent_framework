# src/workflows/scheduled_maintenance_workflow.py
import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Ensure src/ directory is on sys.path for absolute imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../.."))
src_root = os.path.join(project_root, "src")
if src_root not in sys.path:
    sys.path.insert(0, src_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("scheduled_maintenance_workflow")

# Import modules
try:
    # Config
    from src.config.settings import SUPABASE_URL, SUPABASE_KEY
    
    # Machine clustering
    from agents.maintenance.analytics.Scheduled_Maintenance.MachineCluster import run_analysis
    from agents.maintenance.analytics.Scheduled_Maintenance.machine_cluster_interpreter import interpret_results
    
    # Maintenance scheduling
    from agents.maintenance.analytics.Scheduled_Maintenance.maintenance_task_scheduler import MaintenanceTaskScheduler
    from agents.maintenance.analytics.Scheduled_Maintenance.maintenance_task_writer import MaintenanceTaskWriter
    from agents.maintenance.analytics.Scheduled_Maintenance.maintenance_notifier import MaintenanceNotifier
    
    # Database client
    from src.shared_services.supabase_client import SupabaseClient
    
    logger.info("Successfully imported all required modules")
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

class ScheduledMaintenanceWorkflow:
    """
    Scheduled Maintenance Workflow for maintenance data.
    Analyzes machine data to identify maintenance needs and creates scheduled tasks.
    """
    
    def __init__(self):
        """Initialize the scheduled maintenance workflow"""
        try:
            # Set environment variables from settings
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in settings")
                
            os.environ["SUPABASE_URL"] = SUPABASE_URL
            os.environ["SUPABASE_KEY"] = SUPABASE_KEY
            
            self.db = SupabaseClient()
            self.scheduler = MaintenanceTaskScheduler(self.db)
            self.writer = MaintenanceTaskWriter(self.db)
            self.notifier = MaintenanceNotifier()
            logger.info("ScheduledMaintenanceWorkflow initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ScheduledMaintenanceWorkflow: {e}")
            logger.error(traceback.format_exc())
            raise

    def run(self, period_start: Optional[datetime] = None, period_end: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Run the scheduled maintenance workflow:
        1. Fetch machine data
        2. Run machine clustering analysis
        3. Interpret results
        4. Create maintenance tasks
        5. Send notifications
        
        Args:
            period_start: Optional start date for the analysis period
            period_end: Optional end date for the analysis period
            
        Returns a summary of the workflow execution
        """
        result_summary = {
            'analysis_success': False,
            'tasks_created': 0,
            'errors': [],
            'period_start': period_start.isoformat() if isinstance(period_start, datetime) else period_start,
            'period_end': period_end.isoformat() if isinstance(period_end, datetime) else period_end
        }
        
        try:
            # Log analysis period if provided
            if period_start and period_end:
                logger.info(f"Analysis period: {period_start} to {period_end}")
            
            # --- Step 1: Fetch machine data ---
            logger.info("Fetching machine data...")
            
            # Create filters based on date range
            filters = {}
            if period_start and period_end:
                # Convert datetime objects to strings if needed
                start_date_str = period_start.isoformat() if isinstance(period_start, datetime) else period_start
                end_date_str = period_end.isoformat() if isinstance(period_end, datetime) else period_end
                
                # Use the correct filter format for date ranges
                filters['resolved_at.gte'] = start_date_str
                filters['resolved_at.lte'] = end_date_str
                
                logger.info(f"Filtering records by date range: {start_date_str} to {end_date_str}")
            elif period_start:
                start_date_str = period_start.isoformat() if isinstance(period_start, datetime) else period_start
                filters['resolved_at.gte'] = start_date_str
                logger.info(f"Filtering records from {start_date_str} onwards")
            elif period_end:
                end_date_str = period_end.isoformat() if isinstance(period_end, datetime) else period_end
                filters['resolved_at.lte'] = end_date_str
                logger.info(f"Filtering records up to {end_date_str}")

            # Query the database with filters
            records = self.db.query_table(
                table_name="downtime_detail",
                columns="*",
                filters=filters,
                limit=1000
            )
            
            if not records:
                msg = "No machine records found in database for the specified period"
                logger.warning(msg)
                result_summary['errors'].append(msg)
                return result_summary
                
            logger.info(f"Retrieved {len(records)} machine records")
            
            # --- Step 2: Run machine clustering analysis ---
            logger.info("Running machine clustering analysis...")
            analysis_results = run_analysis(records)
            
            if not analysis_results:
                msg = "No results from machine clustering analysis"
                logger.warning(msg)
                result_summary['errors'].append(msg)
                return result_summary
            
            result_summary['analysis_success'] = True
            
            # --- Step 3: Interpret results ---
            logger.info("Interpreting clustering results...")
            machines_to_service = interpret_results(analysis_results)
            
            if not machines_to_service:
                logger.info("No machines identified for maintenance")
                return result_summary
            
            # --- Step 4: Create maintenance tasks ---
            logger.info("Creating maintenance tasks...")
            schedule_results = self.scheduler.schedule_maintenance_tasks(machines_to_service)
            write_results = self.writer.write_maintenance_tasks(schedule_results, self.scheduler)
            
            result_summary['tasks_created'] = write_results.get('tasks_created', 0)
            
            # --- Step 5: Send notifications ---
            if result_summary['tasks_created'] > 0:
                logger.info("Sending maintenance notifications...")
                self.notifier.send_notifications(machines_to_service)
            
            return result_summary
            
        except Exception as e:
            error_msg = f"Error in workflow execution: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            result_summary['errors'].append(error_msg)
            return result_summary


def main():
    """Main entry point for running the scheduled maintenance workflow from command line"""
    logger.info("Starting Scheduled Maintenance Workflow")
    
    import argparse
    parser = argparse.ArgumentParser(description="Run Scheduled Maintenance Workflow")
    parser.add_argument("--start_date", type=str, help="Start date for analysis (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, help="End date for analysis (YYYY-MM-DD)")
    parser.add_argument("--mode", choices=["interactive", "args"], default="interactive", 
                        help="Date selection mode (default: interactive)")
    args = parser.parse_args()
    
    try:
        # Use DateSelector for date range selection
        from agents.maintenance.tools.date_selector import DateSelector
        
        if args.start_date and args.end_date:
            # Use provided dates from command line
            period_start = datetime.strptime(args.start_date, "%Y-%m-%d")
            period_end = datetime.strptime(args.end_date, "%Y-%m-%d")
            logger.info(f"Using specified date range: {period_start.date()} to {period_end.date()}")
        else:
            # Use DateSelector for interactive selection
            start_date_str, end_date_str = DateSelector.get_date_range(mode=args.mode)
            period_start = datetime.strptime(start_date_str, "%Y-%m-%d")
            period_end = datetime.strptime(end_date_str, "%Y-%m-%d")
            logger.info(f"Selected date range: {period_start.date()} to {period_end.date()}")
        
        # For the end date, set it to the end of day (23:59:59) to include all records from that day
        period_end = period_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Initialize and run workflow
        wf = ScheduledMaintenanceWorkflow()
        result = wf.run(
            period_start=period_start,
            period_end=period_end
        )
        
        # Print summary
        print("\n=== Scheduled Maintenance Workflow Summary ===")
        print(f"Analysis period: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")
        print(f"Analysis status: {'Success' if result.get('analysis_success') else 'Failed'}")
        print(f"Tasks created: {result.get('tasks_created', 0)}")
        
        if result.get('errors'):
            print("\nErrors encountered:")
            for error in result['errors']:
                print(f"- {error}")
        
        print("\nWorkflow execution complete.")
        return result
        
    except Exception as e:
        logger.error(f"Unhandled exception in main workflow: {e}")
        logger.error(traceback.format_exc())
        print(f"\nError running workflow: {e}")
        return {'status': 'failed', 'error': str(e)}


if __name__ == '__main__':
    main()