import Compressor from 'compressorjs';
import heic2any from 'heic2any';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

export const CompressPresets = {
    high: {
        quality: 0.95,
        width: 1920,
        height: 1080,
        fit: "outside",
    },
    medium: {
        quality: 0.95,
        width: 576,
        height: 1024,
        fit: "outside",
    },
    low: {
        quality: 1,
        width: 250,
        height: 250,
        fit: "inside",
    }
};

const ImageEntity = class {
    constructor(id, bucketName, highQuality, mediumQuality, thumbnail) {
        this.id = id;
        this.bucketName = bucketName;
        this.highQuality = highQuality;
        this.mediumQuality = mediumQuality;
        this.thumbnail = thumbnail;
    }
};

const is_safari = () => {
    let browserInfo = navigator.userAgent;
    return browserInfo.includes('Safari') && !browserInfo.includes('Chrome');
};

export const compressImage = (image, preset) => {
    return new Promise((resolve, reject) => {
        new Compressor(image, {
            quality: preset.quality,
            maxWidth: preset.width,
            maxHeight: preset.height,
            mimeType: is_safari() ? "image/jpeg" : "image/webp",
            
            success(result) {
                resolve(result);
            },

            error(err) {
                reject(err);
            },
        });
    });
};


export const imageCompressorPipeline = async (image) => {
    try {
        const compressedResults = await Promise.all([
            await compressImage(image, CompressPresets.high),
            await compressImage(image, CompressPresets.medium),
            await compressImage(image, CompressPresets.low),
        ])
        const compressedFiles = {
            "highqualityFile": compressedResults[0],
            "mediumqualityFile": compressedResults[1],
            "thumbnail": compressedResults[2],
        }
        return compressedFiles
    }catch (err) {
        console.error("Error during compression to three states")
    }
}

export const imageProcessor = async (image) => {
    try {
        const compressedFiles = await imageCompressorPipeline(image)
        let id = uuidv4();

        const imageObject = {
            id: id,
            bucketName: "dev",
            highQuality: compressedFiles.highqualityFile.name + "_high",
            mediumQuality:compressedFiles. mediumqualityFile.name + "_medium",
            thumbnail: compressedFiles.thumbnail.name + "_low"
        };
        

        const preparedForUploading = {
            "type": "image",
            "compressedFiles": compressedFiles,
            "imageObject": imageObject,
        }

        return preparedForUploading
       
    } catch (err) {
        console.error("Error in image processing:", err);
    }
};




// export const convertHeicToJpeg = async (blob) => {
//     try {
//         const convertedImage = await heic2any({
//             blob,
//             toType: 'image/jpeg',
//             quality: 1,
//         });
//         return convertedImage;
//     } catch (error) {
//         console.error('Error converting HEIC to JPEG:', error);
//         throw error;
//     }
// };