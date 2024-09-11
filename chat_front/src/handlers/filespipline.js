import { imageProcessor } from "./imageprocessor"
import { videoProccessor } from "./videoprocessor"






const processFile = async (file) => {
    try{
        await fileProcessors[getFileType(file)]
    } catch (err) {
        console.error("Error in uploading files")
    }
}   


const fileProcessors = {
    "image": imageProcessor,
    "video": videoProccessor,
}

const getFileType = (file) => {
    if (file.type.includes("image/")) {
        return "image"
    }
    else if (file.type.includes("video/")) {
        return "video"
    }
}


const uploadImagesToS3 = async (preparedForUploading) => {
    try {
        const response = await axios.post("http://127.0.0.1:5000/images/", imageObject);
        const policies = response.data;
        await uploadImagesToS3(policies, highqualityFile, mediumqualityFile, thumbnail);

        await Promise.all([
            axios.put(policies.high_url, highqualityFile, {
                headers: {
                    "Content-Type": highqualityFile.type
                }
            }),

            axios.put(policies.medium_url, mediumqualityFile, {
                headers: {
                    "Content-Type": mediumqualityFile.type
                }
            }),

            axios.put(policies.thumbnail_url, thumbnail, {
                headers: {
                    "Content-Type": thumbnail.type
                }
            })
        ]);
    } catch (err) {
        console.error("Error uploading to S3:", err);
    }
};


const uploadVideos = async () => {
    pass
} 
