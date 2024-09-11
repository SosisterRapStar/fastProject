// src/components/FileUpload.jsx
import { useDropzone } from 'react-dropzone';
import React, {useCallback, useState} from 'react'
import styles from './dropzone.module.scss'
import { get_thumbnail } from '../handlers/thumbnailer';
import { ArrowUpTrayIcon, XMarkIcon } from '@heroicons/react/24/solid'



function Dropzone() {

  const [files, setFiles] = useState([])


  const filesUpdator = async (acceptedFiles) => {
    const filesWithThumbnails = await Promise.all(
        acceptedFiles.map(async (file) => {
            const thumbnail = await get_thumbnail(file); // Await thumbnail generation
            const url = URL.createObjectURL(thumbnail); // Create URL for the thumbnail
            return Object.assign(file, { thumbnail: url });
        })
    );

    const new_files = [...files, ...filesWithThumbnails];
    return new_files;
  };

  // Modified onDrop to handle the async filesUpdator
  const onDrop = useCallback(async (acceptedFiles) => {
      if (acceptedFiles?.length) {
          const updatedFiles = await filesUpdator(acceptedFiles);
          setFiles(updatedFiles); // Update state with new files
      }
  }, [files]); // Adding `files` as a dependency


  const removeFile = name => {
    setFiles(files => files.filter(file => file.name !== name))
  }

  const {getRootProps, getInputProps, isDragActive} = useDropzone({onDrop})

  return (
    <form>
    <div {...getRootProps()}
      className={`${styles.dropzone} ${isDragActive ? styles.dropzoneActive : ''}`}>
      <input {...getInputProps()} />
      <p className={`${isDragActive ? styles.dropzoneActiveText : styles.dropzoneText}`}>
        {isDragActive ? 'Drop the files here ...' : "Drag 'n' drop some files here, or click to select files"}
      </p>
    </div>
  
    <div className="flex flex-wrap mt-4 gap-2 max-w-[400px]"> {/* Ensure max-w matches the messageFieldContainer */}
      {files.map(file => (
        <div key={file.name} className='relative w-24 h-24'> {/* Fixed size container */}
          <img src={file.thumbnail} className='w-full h-full object-cover rounded-md' /> {/* Maintain aspect ratio */}
          <button
            type='button'
            className='w-7 h-7 bg-gray-600 opacity-50 border border-secondary-400 bg-secondary-400 rounded-full flex justify-center items-center absolute -top-2 -right-2 hover:bg-white transition-colors'
            onClick={() => removeFile(file.name)}
          >
            <XMarkIcon className='w-5 h-5 fill-black hover:fill-secondary-400 transition-colors ' />
          </button>
          <p className='mt-2 text-neutral-500 text-[12px] font-medium text-center'>
            {file.name}
          </p>
        </div>
      ))}
    </div>
  </form>
  
  )
}

export default Dropzone


