import subprocess
import os

def read_docker_logs():
    try:
        # Run docker logs ms_riasec_service
        result = subprocess.run(["docker", "logs", "ms_riasec_service", "--tail", "100"], capture_output=True, text=True, check=True)
        logs = result.stdout + "\n" + result.stderr
        
        # Write to a file in the workspace
        output_path = r"\\wsl.localhost\Ubuntu\home\ba_huan\sketch_app\backend\services\riasec_service\app\docker_logs.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(logs)
        print("Successfully wrote logs to app/docker_logs.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_docker_logs()
