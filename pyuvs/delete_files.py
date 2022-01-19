import argparse
import fnmatch as fnm
import os
import time



def clean_directory(data_path, block):
    """ This cleans the block of directories.

    Args:
        block: an string of 5 digits denoting the orbit block

    Returns:
        nothing. It does the data deletion and tells the user how much time it took to delete the data
    """

    data_location = data_path + block + '/'
    t0 = time.time()
    delete_data(data_location)
    t1 = time.time()
    deletion_time = '{:.2f}'.format(round(t1 - t0, 2))
    print('Deleting all old data in block ' + str(
        block) + ' took ' + deletion_time + ' seconds.')


def delete_data(location):
    """ Delete all the old data.

    Args:
        location: a string of the absolute path to a folder (trailing slash not needed)

    Returns:
        Nothing. It just deletes data
    """

    # Delete xml files
    delete_xml(location)

    # Now get the list of actual data files
    crappy_files = []
    all_files = find_all('*', location)

    all_files = sorted([f.replace('s0', 'a0') for f in all_files])

    # Delete the old files
    last_time_stamp = ''
    last_channel = ''
    for file in all_files:
        current_time_stamp = file[-31:-16]  # Ex. 20190428T115842
        current_channel = file[-35:-32]  # Ex. muv
        if current_time_stamp == last_time_stamp and current_channel == last_channel:
            # Remove s0 files
            if 'a0' in last_file:
                crappy_files.append(last_file.replace('a0', 's0'))
                os.remove(last_file.replace('a0', 's0'))

            # Remove r0 files
            else:
                crappy_files.append(last_file)
                print(last_file)
                #os.remove(last_file)

        # Update my variables
        last_time_stamp = current_time_stamp
        last_channel = current_channel
        last_file = file

    # Remember which old files were deleted
    exclude_old_files(location, get_file_names(crappy_files))


def delete_xml(location):
    """

    Args:
        location:

    Returns:

    """

    # Delete xml files and record their file names
    xml_files = find_all('*.xml', location + '/')
    if xml_files:  # Empty lists are False; non-empty lists are True
        exclude_old_files(location, get_file_names(xml_files))
        for i in xml_files:
            os.remove(i)


def find_all(pattern, path):
    """ Find all files with a specified pattern.

    Args:
        pattern: a Unix-style string to search for. Ex '*.pdf'
        path: a Unix-style string of the path to search for the name. Ex. '/Users/kyco2464/'

    Returns:
        a list of the complete paths containing the pattern

    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnm.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def exclude_old_files(path, files):
    """ Add all files to a list where we can tell rsync to ignore these files in the future.

    Args:
        path: a sting of the folder containing bad files
        files: a list of strings of bad files

    Returns:
        nothing. Make sure user doesn't have to re-download old data after we know it's bad
    """

    # If the file doesn't exist, create it
    if not os.path.exists(path + 'excluded_files.txt'):
        try:
            with open(path + 'excluded_files.txt', 'w'):
                pass
        except OSError:
            print(
                'There was an OSError when trying to make ' + path + 'orbit' + block)
            pass

    # Add old data to a list. Note the 'a' means append, so we guarantee not to overwrite anything.
    with open(path + 'excluded_files.txt', 'a') as f:
        for i in files:
            f.write(i + '\n')


def get_file_names(file_list):
    """

    Args:
        file_list: a list of absolute paths to files. Ex. [/Users/kyco2464/file1.txt, /Users/kyco2464/file2.txt]

    Returns:
        relative_files: a list of just the file names. Ex. [file1.txt, file2.txt]
    """
    relative_files = [fls.split('/')[-1] for fls in file_list]
    return relative_files


if __name__ == '__main__':
    # Start by getting the orbit block from the command line.
    results = add_parser()
    orbit_block = results.orb_block
    data_path = results.data_path

    # Clean the directory of this orbit block.
    clean_directory(data_path, orbit_block)
