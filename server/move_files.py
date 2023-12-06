import os
import shutil

def copy_images_to_target(source_directory, target_directory):
    # Create the target directory if it doesn't exist
    os.makedirs(target_directory, exist_ok=True)
    print(os.listdir(source_directory))
    # Iterate through each file in the source directory
    for x in os.listdir(source_directory):
            print(x)
            for file in os.listdir(source_directory + '/' + x):

                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    source_path = os.path.join(source_directory, file)
                    target_path = os.path.join(target_directory, file)

                    # Copy the image file to the target directory
                    shutil.copy2(source_path, target_path)

    print("All images copied to", target_directory)




# Specify your source and target directories
target_directory = '/Users/sarathsaikrishnadevarakonda/Downloads/facial_emotions_test'
source_directory = '/Users/sarathsaikrishnadevarakonda/Downloads/train_aligned'

# Call the function to move images
copy_images_to_target(source_directory, target_directory)
