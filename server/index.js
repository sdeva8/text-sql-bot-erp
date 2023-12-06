const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);
const copyFile = promisify(fs.copyFile);
const mkdir = promisify(fs.mkdir);

async function organizeImages(rootFolder, destinationFolder) {
  try {
    const folders = await readdir(rootFolder, { withFileTypes: true });

    for (const folder of folders) {
      if (folder.isDirectory()) {
        const folderPath = path.join(rootFolder, folder.name);
        const files = await readdir(folderPath);

        for (const file of files) {
          if (file.endsWith('.jpg')) {
            const folderName = file[0].toLowerCase(); // Use the first character of the filename as the folder name
            const subFolderPath = path.join(destinationFolder, folderName);

            try {
              // Create the folder if it doesn't exist
              await mkdir(subFolderPath, { recursive: true });

              // Find the next available number for the filename
              const existingFiles = await readdir(subFolderPath);
              const imageNumber = existingFiles.length + 1;

              // Construct the new filename
              const newFileName = `${imageNumber}.jpg`;

              // Copy the image to the corresponding folder with the new filename
              await copyFile(path.join(folderPath, file), path.join(subFolderPath, newFileName));
            } catch (error) {
              console.error(`Error processing file ${file}: ${error.message}`);
            }
          }
        }
      }
    }
    console.log('Image organization complete.');
  } catch (error) {
    console.error(`Error reading directory ${rootFolder}: ${error.message}`);
  }
}

// Replace the following paths with your actual paths
const rootFolder = '/Users/sarathsaikrishnadevarakonda/Downloads/face_emotions_raw';

const destinationFolder = '/Users/sarathsaikrishnadevarakonda/Downloads/facial_emotions_test3';

organizeImages(rootFolder, destinationFolder);
