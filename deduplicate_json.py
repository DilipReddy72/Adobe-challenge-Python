import json
from datetime import datetime

# Load JSON file
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['leads']

# Deduplicate records
def deduplicate(records):
    id_map = {}  # Track records by _id
    email_map = {}  # Track records by email
    changes_log = []  # Store change logs

    for record in records:
        record_id = record['_id']
        record_email = record['email']

        # Resolve by _id
        if record_id in id_map:
            id_map[record_id], log = resolve_duplicate(id_map[record_id], record)
            changes_log.extend(log)
        else:
            id_map[record_id] = record

        # Resolve by email
        if record_email in email_map:
            email_map[record_email], log = resolve_duplicate(email_map[record_email], record)
            changes_log.extend(log)
        else:
            email_map[record_email] = record

    # Return deduplicated records and change log
    return list(id_map.values()), changes_log

# Resolve duplicates based on entryDate and position
def resolve_duplicate(existing, new):
    logs = []
    # Compare entryDate
    existing_date = datetime.fromisoformat(existing['entryDate'])
    new_date = datetime.fromisoformat(new['entryDate'])

    if new_date > existing_date:
        logs = generate_change_log(existing, new)
        return new, logs
    elif new_date == existing_date:
        logs = generate_change_log(existing, new)
        return new, logs
    return existing, logs

# Generate change log
def generate_change_log(existing, new):
    log = []
    for key in existing:
        if existing[key] != new[key]:
            log.append({
                'field': key,
                'from': existing[key],
                'to': new[key]
            })
    return log

# Save results to files
def save_output(deduplicated_records, change_log, output_path, log_path):
    with open(output_path, 'w') as output_file:
        json.dump({'leads': deduplicated_records}, output_file, indent=4)

    with open(log_path, 'w') as log_file:
        json.dump(change_log, log_file, indent=4)

# Main function
def main():
    input_file = 'leads.json'  # Input file path
    output_file = 'deduplicated_leads.json'  # Output file path
    log_file = 'change_log.json'  # Log file path

    records = load_json(input_file)
    deduplicated_records, changes_log = deduplicate(records)
    save_output(deduplicated_records, changes_log, output_file, log_file)

    print(f"Deduplication complete. Results saved to {output_file} and {log_file}.")

if __name__ == '__main__':
    main()
