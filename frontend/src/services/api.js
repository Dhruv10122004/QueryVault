import axios from 'axios'
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const checkHealth = async () => {
    const response = await api.get('/health');
    return response.data;
}; 

export const uploadPDF = async(file, onProgess) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgess?.(percentCompleted);
        },
    });

    return response.data;
}

export const uploadYouTube = async (url) => {
    const response = await api.post('/upload/youtube', { url });
    return response.data;
};

export const queryDocuments = async (question, topK = 3) => {
    const response = await api.post('/query', {
        question,
        top_k: topK,
    });
    return response.data;
}

export const clearDatabase = async () => {
    const response = await api.delete('/clear');
    return response.data;
};

export default api;