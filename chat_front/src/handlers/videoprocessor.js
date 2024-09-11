export const videoProccessor = async () => {
    return null
}


const videoThumbnailer = async (videoFile, captureTime = 1) => {
    return new Promise((resolve, reject) => {
        // Create a video element
        const video = document.createElement('video');
        video.preload = 'metadata';

        // Create a canvas element
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // Create an object URL for the video file
        const url = URL.createObjectURL(videoFile);
        video.src = url;

        // Load video metadata to set canvas dimensions
        video.onloadeddata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Set the current time to the capture time
            video.currentTime = captureTime;
        };

        // Once the video seeks to the capture time, draw the frame on the canvas
        video.onseeked = () => {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

            // Convert canvas to a blob
            canvas.toFile(blob => {
                if (blob) {
                    resolve(blob); // Resolve the promise with the blob
                } else {
                    reject(new Error('Failed to create a thumbnail from the video.'))
                }
                URL.revokeObjectURL(url)
            }, 'image/jpeg')
        };

        
        video.onerror = (error) => {
            reject(new Error('Error loading video: ' + error.message))
            URL.revokeObjectURL(url) 
        };
    });
};



const videoProccessor = async (video) => {
    const videThumbnail = await videoThumbnailer(video)
    const compressedFiles = await imageCompressorPipeline(videoThumbnail)
    return new Promise((resolve, reject) => {
        
    })
}
