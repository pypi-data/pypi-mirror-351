import argparse
import tarfile
import hashlib
import os

def get_tar_file_size_in_mb(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)

def diff(base_tar_path, new_tar_path, output_tar_path):
    with tarfile.open(output_tar_path, 'w') as diff_tar:
        # Add files that are in the new image but not in the base image
        with tarfile.open(new_tar_path, 'r') as new_tar:
            with tarfile.open(base_tar_path, 'r') as base_tar:            
                base_files = {member.name: member for member in base_tar.getmembers()}
                new_files = {member.name: member for member in new_tar.getmembers()}
                
                for member in new_tar.getmembers():
                    if member.name in new_files and member.name not in base_files:
                        # Add new files that are not in the base image
                        if member.isfile() or member.issym() or member.islnk():
                            diff_tar.addfile(member, new_tar.extractfile(member))
                        else:
                            diff_tar.addfile(member)
                    else:
                        # In case new_files and base_files both contain the file
                        base_member = base_files.get(member.name)
                        new_member = new_files.get(member.name)
                        if base_member.size != new_member.size:
                            # If file size has changed, add it to the diff tar
                            if member.isfile() or member.issym() or member.islnk():
                                diff_tar.addfile(new_member, new_tar.extractfile(new_member))
                            else:
                                diff_tar.addfile(new_member)
                        else:
                            # In case file size is the same
                            if member.isfile() or member.issym() or member.islnk():
                                # Calculate file hash to check for content changes
                                with new_tar.extractfile(new_member) as new_file:
                                    new_hash = hashlib.sha256(new_file.read()).hexdigest()
                                with base_tar.extractfile(base_member) as base_file:
                                    base_hash = hashlib.sha256(base_file.read()).hexdigest()
                                
                                if new_hash != base_hash:
                                    diff_tar.addfile(new_member, new_tar.extractfile(new_member))
                            else:
                                # If it's a directory or other type, just add it
                                diff_tar.addfile(new_member)
    # summary of file sizes
    print("Base image size: {} MB".format(get_tar_file_size_in_mb(base_tar_path)))
    print("New image size: {} MB".format(get_tar_file_size_in_mb(new_tar_path)))
    print("Diff image size: {} MB".format(get_tar_file_size_in_mb(output_tar_path)))
                                

def merge(base_tar_path, diff_tar_path, new_tar_path):
    # merge the diff.tar with the base image
    with tarfile.open(diff_tar_path, 'r') as diff_tar:
        with tarfile.open(base_tar_path, 'r') as base_tar:
            with tarfile.open(new_tar_path, 'w') as new_tar:
                # Add base files
                for member in base_tar.getmembers():
                    if member.isfile() or member.issym() or member.islnk():
                        new_tar.addfile(member, base_tar.extractfile(member))
                    else:
                        new_tar.addfile(member)

                # Add diff files
                for member in diff_tar.getmembers():
                    if member.isfile() or member.issym() or member.islnk():
                        new_tar.addfile(member, diff_tar.extractfile(member))
                    else:
                        new_tar.addfile(member)
    
    print("Merge completed.")


def main():
    # subcommand parser
    parser = argparse.ArgumentParser(description="Docker image diff tool")
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    # diff command
    diff_parser = subparsers.add_parser('diff', help='Create a diff tar from two Docker image tars')
    diff_parser.add_argument('--base', required=True, help='Path to base image tar')
    diff_parser.add_argument('--new', required=True, help='Path to new image tar')
    diff_parser.add_argument('--output', required=True, help='Where to write diff.tar')
    # merge command
    merge_parser = subparsers.add_parser('merge', help='Merge a diff tar with a base image tar')
    merge_parser.add_argument('--base', required=True, help='Path to base image tar')
    merge_parser.add_argument('--diff', required=True, help='Path to diff tar')
    merge_parser.add_argument('--output', required=True, help='Where to write new image tar')
    args = parser.parse_args()
    if args.command == 'diff':
        diff(args.base, args.new, args.output)
    elif args.command == 'merge':
        merge(args.base, args.diff, args.output)

if __name__ == "__main__":
    main()
