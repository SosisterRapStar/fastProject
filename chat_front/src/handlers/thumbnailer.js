
import {compressImage, CompressPresets} from './imageprocessor'

export const get_thumbnail = async (file) => {
    try {
        const compressedImage = await compressImage(file, CompressPresets.low);
        return compressedImage; 
    } catch (error) {
        console.error('Error compressing image:', error);
        throw error; 
    }
};


