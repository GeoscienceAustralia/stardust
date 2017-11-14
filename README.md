# Stardust
Remove all AWS items created with terraform in the event of a poisoned or lost .tfstate file

## Usage
python3 fire.py stack_name -d

## Notes
This is a simple script that doesn't understand dependancies, so it may need to be altered if you have resources that must be deleted in a certain order (eg security groups that are dependant on security groups).

## License
This code is licensed under a Apache 2.0 license. See the [license deed](LICENSE) for details

## Contaces
**Tom Butler**  
*Lead Devloper*  
<tom.butler@ga.gov.au>  
