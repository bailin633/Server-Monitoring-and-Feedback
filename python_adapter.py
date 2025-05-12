import sys
import json
import os

# Add the current script's directory to Python path to find other modules
# This might not be strictly necessary if Electron's CWD is the project root,
# but it's a good practice for robustness.
# script_dir = os.path.dirname(os.path.abspath(__file__))
# if script_dir not in sys.path:
#     sys.path.append(script_dir)

# Import functions from your existing Python files
try:
    from windows_info import (
        get_cpu_usage, get_memory_usage, get_os_info,
        get_windows_version_info, get_cpu_core_count,
        get_virtual_memory_usage, get_running_process_count, get_mem_info
    )
    from send_email import send_alert_email
    from config import read_config_main, save_config
    from main import run_initial_setup # Import the setup function
    # Import other necessary functions or modules here
except ImportError as e:
    print(json.dumps({"error": f"Failed to import a required Python module: {e}"}))
    sys.exit(1)

def dispatch(action, args_dict=None):
    """
    Dispatches the action to the corresponding Python function.
    action (str): The name of the function to call.
    args_dict (dict, optional): A dictionary of arguments for the function.
    """
    if args_dict is None:
        args_dict = {}

    try:
        if action == "get_cpu_usage":
            return get_cpu_usage()
        elif action == "get_memory_usage":
            return get_memory_usage()
        elif action == "get_os_info":
            return get_os_info() # Returns a tuple (name, version)
        elif action == "get_windows_version_info":
            return get_windows_version_info()
        elif action == "get_cpu_core_count":
            return get_cpu_core_count() # Returns a tuple (cores, logical_cores)
        elif action == "get_virtual_memory_usage":
            return get_virtual_memory_usage()
        elif action == "get_running_process_count":
            return get_running_process_count()
        elif action == "get_mem_info": # Physical memory in GB
            return get_mem_info()
        elif action == "read_config":
            # read_config_main returns: email, password, target_email, last_user_time, user_clear_time, cpu_threshold, memory_threshold, email_cooldown
            email, password, target_email, last_user_time, user_clear_time, cpu_threshold, memory_threshold, email_cooldown = read_config_main()
            return {
                "sender_email": email,
                "sender_password": password, # Be cautious about sending passwords
                "receiver_email": target_email,
                "check_interval_minutes": last_user_time,
                "clear_console_seconds": user_clear_time,
                "cpu_threshold": cpu_threshold,
                "memory_threshold": memory_threshold,
                "email_cooldown": email_cooldown # 新增
            }
        elif action == "save_config":
            # Expects: sender_email, sender_password, receiver_email, check_interval_minutes, clear_console_seconds, cpu_threshold, memory_threshold, email_cooldown
            required_keys = ["sender_email", "sender_password", "receiver_email", "check_interval_minutes", "clear_console_seconds", "cpu_threshold", "memory_threshold", "email_cooldown"]
            if not all(key in args_dict for key in required_keys):
                return {"error": "Missing required arguments for save_config", "required": required_keys}
            
            success = save_config(
                args_dict["sender_email"],
                args_dict["sender_password"],
                args_dict["receiver_email"],
                args_dict["check_interval_minutes"],
                args_dict["clear_console_seconds"],
                args_dict["cpu_threshold"],
                args_dict["memory_threshold"],
                args_dict["email_cooldown"] # 新增
            )
            return {"success": success}
        elif action == "send_alert_email":
            # Expects: subject, body, to_email, from_email, from_password
            required_keys = ["subject", "body", "to_email", "from_email", "from_password"]
            if not all(key in args_dict for key in required_keys):
                 return {"error": "Missing required arguments for send_alert_email", "required_keys": required_keys}
            
            # send_alert_email now returns a dictionary like {"success": True/False, "message/error": "..."}
            email_send_result = send_alert_email(
                args_dict["body"],
                args_dict["subject"],
                args_dict["to_email"],
                args_dict["from_email"],
                args_dict["from_password"]
            )
            return email_send_result # Directly return the result dictionary
        elif action == "run_initial_setup":
            run_initial_setup() # Call the imported function
            return {"success": True, "message": "Initial Python setup executed."}
        else:
            return {"error": f"Unknown action: {action}"}
    except Exception as e:
        # Capture any other exceptions during function execution
        return {"error": f"Error executing action '{action}': {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action_to_perform = sys.argv[1]
        
        # Subsequent arguments can be passed as a JSON string
        # For simplicity now, we'll assume specific actions might have specific arg needs
        # or main.js will pass a JSON string as the second argument for 'args_dict'
        
        action_args_dict = {}
        if len(sys.argv) > 2:
            try:
                action_args_dict = json.loads(sys.argv[2])
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON arguments provided."}))
                sys.exit(1)

        result = dispatch(action_to_perform, action_args_dict)
        print(json.dumps(result)) # Output result as JSON
    else:
        print(json.dumps({"error": "No action specified."}))
        sys.exit(1)