import boto3

def lambda_handler(event, context):
    
    '''
    ### This function is to create tag key names for existing instances in DEV & DR VPC
    ###  from pre-defined required tags.  EXT VPC is excluded for now.  
    ### 
    ### Function will check:
    ### 1. Create a dictionary contains instance ids and vpc ids
    ### 2. Crosscheck to find out if instances have tag keys from required tags list
    ### 3. If instance(s) is missing required tag(s), it will add required tag key name(s)
    ### 4. If instance(s) has all required tags, it will skip.
    '''
    
    # Creating list of required tag keys, total of 9 tag keys
    required_tags = ['Creator', 'CreateDate', 'Name', 'Domain', 'BusinessOwner', 'Description', 'Backup', 'RunSchedule', 'Cost']
    
    # Creating variable for EXT VPC.  Instances in EXT VPC is excluded.
    ext_vpc = 'vpc-9904d7f2'
    
    # Calling EC2 Boto funciton to get EC2 info
    client = boto3.client('ec2')
    instance_info = client.describe_instances()
    
    # Creating empty dictionary to store instance ids and vpc ids in key/value pair
    instances_vpc = {}
    
    # Getting all instance ids and vpc ids in DEV and DR then adding them to empty dictionary as key/value
    for reservation in instance_info["Reservations"]:
        for instance in reservation["Instances"]:
            if instance["VpcId"] != ext_vpc:
                instances_vpc[instance["InstanceId"]] = instance["VpcId"]
   
    # Log output of total number of instance
    print("\nTotal Number of EC2 Instances: "+ str(len(instances_vpc))+'\n')
    
    # Getting existing tag key names of all instaces
    for iid in instances_vpc.keys():
        all_tags = client.describe_tags(Filters = [{'Name': 'resource-id', 'Values': [iid]}])
        instance_tags = []
        for tag_info in all_tags['Tags']:
            instance_tags.append(tag_info['Key'])
        
        # Comparing two lists to find common tag key name(s)
        common_tags = list(set(required_tags) & set(instance_tags))
        
        # Finding missing tag key name(s)
        missing_tags = list(set(required_tags) - set(common_tags))
        
        # Creating tag key(s).  If instance(s) has all required tag keys, it will skip.
    #     if missing_tags == []:
    #         print(str(iid) + ' has all required tags!')
    #     else:
    #         print(str(iid) + ' is missing required tags: ' + str(missing_tags))
    #         for key_name in missing_tags:
    #             tagging_keys = client.create_tags(Resources=[iid], Tags=[{'Key': key_name, 'Value': ''}])
    #         print('Added missing tags.\n')

    # print("\nAll instances in DEV and DR VPC have required tags.\n")
    return True
