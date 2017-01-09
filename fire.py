#!/usr/bin/env python3
"""
This module will remove all aws items tagged with createdby=terraform
"""


from __future__ import print_function
import boto3
import argparse

def delete_instances(filters, dry_run):
    """
    Remove all instances with filtered tags
    """
    # Create an EC2 Client
    client = boto3.client('ec2')
    instance_ids = []

    if dry_run:
        print("Instances marked for removal")
    else:
        print("Removing instances")
    ec2s = client.describe_instances(Filters=filters)
    for ec2 in ec2s['Reservations']:
        for instance in ec2['Instances']:
            instance_id = instance['InstanceId']
            instance_ids.append(instance_id)
            print(instance_id)
            if not dry_run:
                client.terminate_instances(InstanceIds=[instance_id])


    if not dry_run:
        # Wait for the instances to change their state to terminated
        if len(instance_ids) > 0:
            print('Waiting for instances to terminate')
            waiter = client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=instance_ids)
            print("done")

def delete_vpc(filters, stack_name, dry_run):
    """
    Remove the specified VPC
    """

    # Create an EC2 Client
    client = boto3.client('ec2')

    # Get the VPC Id
    vpcs = client.describe_vpcs(Filters=filters)
    for vpc in vpcs['Vpcs']:
        vpc_id = vpc['VpcId']

        # Delete the Security Group
        if dry_run:
            print("Security groups marked for removal")
        else:
            print("Removing security groups")

 # Delete the NAT gateways
        if dry_run:
            print("NAT gateways marked for removal")
        else:
            print("Removing NAT gateways")
        subnets = client.describe_subnets(Filters=filters)
        for subnet in subnets['Subnets']:
            nat_filters = [{'Name':'subnet-id', 'Values':[subnet['SubnetId']]}]
            ngws = client.describe_nat_gateways(Filters=nat_filters)
            for ngw in ngws['NatGateways']:
                print(ngw['NatGatewayId'])
                if not dry_run:
                    client.delete_nat_gateway(NatGatewayId=ngw['NatGatewayId'])

# Detach and delete the internet gateway
        if dry_run:
            print("Internet gateways marked for removal")
        else:
            print("Removing internet gateways")
        igws = client.describe_internet_gateways(Filters=filters)
        for igw in igws['InternetGateways']:
            print(igw['InternetGatewayId'])
            if not dry_run:
                client.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=igw['Attachments'][0]['VpcId'])
                client.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])

        # Delete the subnet
        if dry_run:
            print("Subnets marked for removal")
        else:
            print("Removing subnets")
        subnets = client.describe_subnets(Filters=filters)
        for subnet in subnets['Subnets']:
            print(subnet['SubnetId'])
            if not dry_run:
                client.delete_subnet(SubnetId=subnet['SubnetId'])

        #Remove the ssh_from_jump sec groups first
        print('ssh_from_jump')
        sg_filters = [{'Name':'tag:Name', 'Values':[stack_name + '-ssh_from_jump']}]
        sec_groups = client.describe_security_groups(Filters=sg_filters)
        for sec_group in sec_groups['SecurityGroups']:
            print(sec_group['GroupId'])
            if not dry_run:
                client.delete_security_group(GroupId=sec_group['GroupId'])
        print('other')
        sec_groups = client.describe_security_groups(Filters=filters)
        for sec_group in sec_groups['SecurityGroups']:
            print(sec_group['GroupId'])
            if not dry_run:
                client.delete_security_group(GroupId=sec_group['GroupId'])

                # Delete the route table
        if dry_run:
            print("Route tables marked for removal")
        else:
            print("Removing route tables")
        route_tables = client.describe_route_tables(Filters=filters)
        for route_table in route_tables['RouteTables']:
            print(route_table['RouteTableId'])
            if not dry_run:
                client.delete_route_table(RouteTableId=route_table['RouteTableId'])

        if dry_run:
            print("Subnets marked for removal")
        else:
            print("Removing subnets")
        subnets = client.describe_subnets(Filters=filters)
        for subnet in subnets['Subnets']:
            print(subnet['SubnetId'])
            if not dry_run:
                client.delete_subnet(SubnetId=subnet['SubnetId'])

        # Delete the VPC
        if dry_run:
            print("VPC marked for removal")
        else:
            print("Removing VPC")
        print(vpc_id)
        if not dry_run:
            client.delete_vpc(VpcId=vpc_id)


def main():
    """
    Parse Args
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("stack_name", help="The value of the stack_name tag")
    parser.add_argument("-d",
                        "--dryrun",
                        help="Dry Run (don't delete anything)",
                        action="store_true")
    args = parser.parse_args()

    # Define the search filter
    filters = [{'Name':'tag:created_by', 'Values':['terraform']},
               {'Name':'tag:stack_name', 'Values':[args.stack_name]}]
    delete_instances(filters, args.dryrun)
    delete_vpc(filters, args.stack_name, args.dryrun)


if __name__ == "__main__":
    main()
