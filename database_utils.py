class DatabaseConnector:

    def __init__(self, path):
        self.path = path
    
    def read_db_creds(self):
        dict = {}
        with open(path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    key, value = line.split(':', 1)
                    dict[key.strip()] = value.strip()
        print(dict)

path = 'db_creds.yaml'
connector = DatabaseConnector(path)
connector.read_db_creds()
    
