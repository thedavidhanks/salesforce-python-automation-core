import json
import os
import subprocess

from dotenv import load_dotenv

# Create a function that will run the terminal command sf org login jwt.  
#   utilize variables specified by .env
#  sf org login jwt --username=$SF_USERNAME --client-id=$CLIENT_ID --jwt-key-file=./resources/keys/server.key --set-default --alias=prod
def sf_login(user=None, client_id=None, key_file=None):
	"""
	Logs into a Salesforce org using JWT-based authentication.

	Parameters:
		user (str): Salesforce username. defaults to SF_USERNAME
		client_id (str): Salesforce connected app client ID. defaults to CLIENT_ID
		key_file (str): Path to the JWT key file (default: './resources/keys/server.key'). defaults to SERVER_KEY_FILE

	Usage:
		sf_login('user@example.com', 'CLIENT_ID', './resources/keys/server.key')
	"""	

	load_dotenv()

	if user is None:
		user = os.getenv("SF_USERNAME")
	if client_id is None:
		client_id = os.getenv("CLIENT_ID")
	if key_file is None:
		key_file = os.getenv("SERVER_KEY_FILE") or './resources/keys/server.key'

	if not user or not client_id:
		raise ValueError("SF_USERNAME and CLIENT_ID must be set as arguments or in the .env file.")

	cmd = [
		"sf", "org", "login", "jwt",
		f"--username={user}",
		f"--client-id={client_id}",
		f"--jwt-key-file={key_file}",
		"--set-default",
		"--alias=prod"
	]
	subprocess.run(cmd, check=True)

def sf_logout():
	"""
	Logs out of the Salesforce org.
	sf org logout --target-org me@my.org
	"""
	cmd = ["sf", "org", "logout", "--target-org", "prod", "--no-prompt"]
	try:
		subprocess.run(cmd, check=True)
		print("Logged out successfully.")
	except subprocess.CalledProcessError as e:
		print(f"An error occurred while logging out: {e}")

def sf_query(query: str, verbosity: int=1):
	"""
	Runs a SOQL query against the Salesforce org and returns the results as a JSON object.

	Parameters:
		query (str): The SOQL query to run.
		verbosity (int): Verbosity level for logging. Defaults to 1 (errors only).

	Returns:
		dict: The results of the query as a dictionary.
	"""
	cmd = ["sf", "data", "query", "--query", query, "--json"]
	try:
		result = subprocess.run(cmd, check=True, capture_output=True, text=True)
		data = json.loads(result.stdout)
		if verbosity >= 5:
			print(f"Query result: {data}")
		return data
	except subprocess.CalledProcessError as e:
		if verbosity >= 1:
			print(f"An error occurred while running the query: {e}")
		return {}

def get_record_count(object_name: str, verbosity: int=1):
	"""
	Retrieves the count of records for a specified object in the Salesforce org.

	sf_query returns a dictionary with the result.totalSize key containing the count.
	{'status': 0, 'result': {'records': [], 'totalSize': 38300, 'done': True}, 'warnings': []}

	Parameters:
		object_name (str): The name of the object to count records for.
		verbosity (int): Verbosity level for logging. Defaults to 1 (errors only).

	Returns:
		int: The count of records in the object, or None if an error occurs.
	"""
	query = f"SELECT COUNT() FROM {object_name}"
	result = sf_query(query, verbosity=verbosity)
	if result and 'totalSize' in result.get('result', {}):
		return result['result']['totalSize']
	return None

def download_object(object_name: str, folder: str="", file_type: str="csv", check_exists: bool=True, saveFields: bool=False, get_id: bool=False, verbosity: int=1, saveEmptyObjects: bool=False):
	"""
	Downloads csv of specified object from the Salesforce org.

	get_id: bool=False
		When true, the function will use the --async option and get the ID of the job rather than waiting for the job to complete.

	EX sf data export bulk --query "SELECT Id, Name, Account.Name FROM Contact" --output-file export-accounts.csv --wait 10 --target-org my-scratch
	REFERENCE:
		https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_data_commands_unified.htm#cli_reference_data_export_bulk_unified
	"""
	download_folder = "downloads"

	if check_exists:
		isReal = verify_object_in_org(object_name)

		if isReal:
			if verbosity >= 5:
				print(f"download_object: Object {object_name} exists in the org. Proceeding with download.")
		if not isReal:
			if verbosity >= 1:
				print(f"download_object: Object {object_name} does not exist in the org. Please verify the object name.")
			return False
	
	if not saveEmptyObjects:
		# Check if the object has any records
		record_count = get_record_count(object_name, verbosity=verbosity)
		if record_count is None or record_count == 0:
			if verbosity >= 2:
				print(f"download_object: Object {object_name} has no records. Skipping download.")
			return False
	
	field_list = get_fields_on_obj(object_name, saveJSON=saveFields)
	if not field_list:
		if verbosity >= 1:
			print(f"download_object: No fields found for object {object_name}.  Download aborted.")
		return False
	# Create the query string with all fields
	fields_query = ', '.join(field_list)
	# Construct the query to select all fields from the object	
	
	if folder and folder not in ["", None]:
		# Ensure the folder exists
		if not os.path.exists(folder):
			os.makedirs(folder)
	else:
		# if the folder is None, then use the download folder
		folder = download_folder

	# Configure the sf command to download the object	
	query = f"SELECT {fields_query} FROM {object_name}"
	# async_wait_cmd = "--async" if get_id else "--wait 1"
	cmd = ["sf", "data", "export", "bulk", "--query", query, "--output-file", f"{folder}/{object_name}.{file_type}","--result-format", file_type]

	if verbosity >= 5:
		print(f"$: {' '.join(cmd)}")
		print(f"\tDownloading {object_name} as {file_type} to {folder}/{object_name}.{file_type}")

	try:
		# Run the command
		if get_id:
			v = subprocess.run(cmd, check=True, capture_output=True)

			output = v.stdout.decode('utf-8')
			job_id = extract_job_id(output)
			return job_id
		else:
			# Run the command and wait for it to complete
			print(f"Downloading {object_name} as {file_type}...")
			subprocess.run(cmd, check=True)
		
		# Print the output of the command
		if verbosity >= 3:
			print(f"Object {object_name} downloaded successfully as {file_type}.")
	except subprocess.CalledProcessError as e:
		if verbosity >= 1:
			print(f"An error occurred while downloading the object {object_name}: {e}")
		return False
	
def extract_job_id(output: str) -> str:
    """
    Extracts the Job ID from Salesforce CLI async export output.
    
    Args:
        output (str): The stdout output from sf data export bulk command with --async flag
        
    Returns:
        str: The Job ID (e.g., '750Wj00000MY3bVIAT') or None if not found
    """
    import re
    
    # Look for "Job Id:" followed by whitespace and capture the job ID
    # Job IDs are typically 15 or 18 characters long and alphanumeric
    pattern = r'Job Id:\s*\n\s*([A-Za-z0-9]{15,18})'
    
    match = re.search(pattern, output)
    if match:
        return match.group(1)
    
    return None

def get_job_status(job_id: str, verbosity: int = 1):
    """
    Gets the status of a Salesforce data export job.
    
    Args:
        job_id (str): The Job ID to check status for (e.g., '750Wj00000MY3bVIAT')
        verbosity (int): Verbosity level for output (default: 1)
        
    Returns:
        dict: Dictionary containing job status information with keys:
            - 'status': Job status (e.g., 'JobComplete', 'InProgress', 'Failed')
            - 'state': Job state 
            - 'job_id': The job ID
            - 'raw_output': Full command output
        Returns None if command fails or output cannot be parsed
    """
    import json

    cmd = ["sf", "data", "export", "resume", "--job-id", job_id, "--json"]

    if verbosity >= 3:
        print(f"Checking status for job: {job_id}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        output = result.stdout
        
        if verbosity >= 5:
            print(f"Raw output: {output}")
        
        # Parse JSON output
        data = json.loads(output)
        
        # Extract relevant status information
        status_info = {
            'status_no': data.get('status', 'Unknown'),
			'status': 'Completed' if data.get('status','Unknown') == 0 else 'InProgress',
            'size': data.get('result', {}).get('totalSize', 'Unknown'), 
            'job_id': job_id,
			'warnings': data.get('warnings', []),
			'filePath': data.get('result', {}).get('filePath', 'Unknown'),
            'raw_output': output
        }
        
        if verbosity >= 2:
            print(f"Job {job_id} status: {status_info['status']}")
        
        return status_info
        
    except subprocess.CalledProcessError as e:
        if verbosity >= 1:
            print(f"Error checking job status for {job_id}: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr.decode('utf-8')}")
        return None
    except json.JSONDecodeError as e:
        if verbosity >= 1:
            print(f"Error parsing JSON output for job {job_id}: {e}")
        return None
    except Exception as e:
        if verbosity >= 1:
            print(f"Unexpected error checking job status for {job_id}: {e}")
        return None
	
def get_object_list(saveJSON=False):
	"""
	Retrieves a list of objects from the Salesforce org.
	`SELECT QualifiedApiName FROM EntityDefinition`
	"""
	cmd = ["sf", "data", "query", "--query", "SELECT QualifiedApiName FROM EntityDefinition WHERE IsQueryable = true AND IsRetrieveable = true AND KeyPrefix != null","--json"]
	try:
		# Run the command and store the result in a variable
		v = subprocess.run(cmd, check=True, capture_output=True)
		
		# Decode the output from bytes to string
		output = v.stdout.decode('utf-8')
		
		# Parse the JSON output to get the list of objects
		data = json.loads(output)
		
		# save data to a file
		if saveJSON:
			# Ensure the downloads directory exists
			if not os.path.exists("downloads"):
				os.makedirs("downloads")
			
			# Save the JSON data to a file in the downloads directory
			with open("object_list.json", "w") as f:
				json.dump(data, f, indent=4)
				
		# Extract the list of objects from the JSON data
		object_list = [item['QualifiedApiName'] for item in data['result']['records']]
		
		return object_list
	except subprocess.CalledProcessError as e:
		print(f"An error occurred while retrieving the object list: {e}")
		return []
	

def verify_object_in_org(object_name: str) -> bool:
	"""
	Verifies if the specified object exists in the Salesforce org.
	"""
	cmd = ["sf", "data", "query", "--query", f"SELECT Id FROM {object_name} LIMIT 1","--json"]
	try:
		# Run the command and store the result in a variable
		v = subprocess.run(cmd, check=True, capture_output=True)

		# print(f"Command output: {v.stdout.decode('utf-8')}")
		# print(type(v.stdout))
		# subprocess.run(cmd, check=True)
		return True
	except subprocess.CalledProcessError:
		return False

def get_fields_on_obj(object_name: str, ignore_compound: bool=True, saveJSON: bool=False):
	"""
	INPUTS:
		ignore_compound: bool=True
			Whether to ignore compound fields (fields that are not directly queryable).
	Retrieves the fields of a specified object in the Salesforce org.
		SELECT EntityDefinition.QualifiedApiName, QualifiedApiName, DataType
		FROM FieldDefinition
		WHERE EntityDefinition.QualifiedApiName = 'Account'
	"""	
	query = f"SELECT QualifiedApiName, IsApiFilterable, IsCompound FROM FieldDefinition WHERE EntityDefinition.QualifiedApiName = '{object_name}'"
	if ignore_compound:
		query += " AND IsCompound = false"
	cmd = ["sf", "data", "query", "--query", query,"--json"]
	try:
		v = subprocess.run(cmd, check=True, capture_output=True)
		output = v.stdout.decode('utf-8')
		data = json.loads(output)

		if saveJSON:
			# Save the JSON data to a file in the downloads directory
			if not os.path.exists("downloads"):
				os.makedirs("downloads")
			with open(f"downloads/{object_name}_fields.json", "w") as f:
				json.dump(data, f, indent=4)
		fields = [item['QualifiedApiName'] for item in data['result']['records']]
		return fields
	except subprocess.CalledProcessError as e:
		print(f"An error occurred while retrieving fields for {object_name}: {e}")
		return []