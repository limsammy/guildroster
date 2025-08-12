import apiClient from './config';

export interface ImportResponse {
  message: string;
  results: {
    [key: string]: {
      imported: number;
      errors: string[];
    };
  };
}

export class ImportService {
  /**
   * Import data from a file
   * @param file - The file to import (ZIP or JSON)
   * @returns Import response with results
   */
  static async importData(file: File): Promise<ImportResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post<ImportResponse>('/data-import/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  /**
   * Get import/export status
   */
  static async getStatus(): Promise<{
    import_enabled: boolean;
    export_enabled: boolean;
    supported_formats: string[];
    supported_data_types: string[];
  }> {
    const response = await apiClient.get('/data-import/export-status');
    return response.data;
  }
}

