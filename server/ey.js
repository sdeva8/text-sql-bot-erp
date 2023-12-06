const fs = require('fs');
const path = require('path');

function getImagePaths(directory) {
  const imagePaths = [];

  // Iterate through subfolders in the directory
  fs.readdirSync(directory, { withFileTypes: true }).forEach(subfolder => {
    if (subfolder.isDirectory()) {
      // Get the full path to the subfolder
      const subfolderPath = path.join(directory, subfolder.name);

      // Iterate through files in the current subfolder
      fs.readdirSync(subfolderPath).forEach(filename => {
        const filePath = path.join(subfolder.name, filename);
        
        // Check if the file is an image (you can customize this check based on your file types)
        if (filename.toLowerCase().endsWith('.jpg') || filename.toLowerCase().endsWith('.png')) {
          imagePaths.push(filePath);
        }
      });
    }
  });

  return imagePaths;
}

const rootDirectory = '/Users/sarathsaikrishnadevarakonda/Downloads/train_aligned';
const rawDirectory = '/Users/sarathsaikrishnadevarakonda/Downloads/face_emotions_raw';

const rootImagePaths = (getImagePaths(rootDirectory).sort());
const rawImagePaths = (getImagePaths(rawDirectory).sort())
// console.log(rootImagePaths);
// console.log(rawImagePaths);

function compareAndRename(rawPaths, rootPaths) {
    // Sort both arrays to ensure a consistent order
    rootPaths.sort();
    rawPaths.sort();
  
    // Iterate through each pair of paths and rename the file in the raw directory
    for (let i = 0; i < rawPaths.length; i++) {
      const rootPath = rootPaths[i];
      const rawPath = rawPaths[i];
  
      const rootFileName = path.basename(rootPath);
      const rawFileName = path.basename(rawPath);
      const rawFolder = path.dirname(rawPath);
  
      // Rename the file in the raw directory to match the root file name
      const newRawPath = path.join(rawFolder, rootFileName);
  
      try {
        fs.renameSync(rawDirectory + '/'+rawPath, rawDirectory + '/'+newRawPath);
        console.log(`Renamed: ${rawFileName} -> ${rootFileName}`);
      } catch (error) {
        console.error(`Error renaming file: ${error.message}`);
      }
    }
  }
  compareAndRename(rawImagePaths,rootImagePaths)