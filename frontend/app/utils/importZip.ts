import JSZip from 'jszip';

export interface ImportedData {
  id: string;
  exported_at: string;
  data: any[];
}

export interface ImportResult {
  success: boolean;
  message: string;
  importedData?: { [key: string]: ImportedData };
  errors?: string[];
}

export async function importResourcesFromZip(file: File): Promise<ImportResult> {
  try {
    const zip = new JSZip();
    const zipContent = await zip.loadAsync(file);
    
    const importedData: { [key: string]: ImportedData } = {};
    const errors: string[] = [];
    
    // Process each JSON file in the zip
    for (const [filename, zipEntry] of Object.entries(zipContent.files)) {
      if (filename.endsWith('.json') && !zipEntry.dir) {
        try {
          const jsonContent = await zipEntry.async('string');
          const parsedData: ImportedData = JSON.parse(jsonContent);
          
          // Validate the imported data structure
          if (!parsedData.id || !parsedData.data) {
            errors.push(`Invalid data structure in ${filename}: missing id or data field`);
            continue;
          }
          
          importedData[parsedData.id] = parsedData;
        } catch (parseError) {
          errors.push(`Failed to parse ${filename}: ${parseError}`);
        }
      }
    }
    
    if (Object.keys(importedData).length === 0) {
      return {
        success: false,
        message: 'No valid data files found in the ZIP file',
        errors
      };
    }
    
    return {
      success: true,
      message: `Successfully imported ${Object.keys(importedData).length} data types`,
      importedData,
      errors: errors.length > 0 ? errors : undefined
    };
  } catch (error) {
    return {
      success: false,
      message: `Failed to process ZIP file: ${error}`,
      errors: [error as string]
    };
  }
}

export async function importResourcesFromJson(file: File): Promise<ImportResult> {
  try {
    const content = await file.text();
    const data = JSON.parse(content);
    
    const importedData: { [key: string]: ImportedData } = {};
    const errors: string[] = [];
    
    // Handle both single resource format and multi-resource format
    if (data.id && data.data) {
      // Single resource format
      importedData[data.id] = data;
    } else {
      // Multi-resource format (from exportAllAsJson)
      for (const [key, resourceData] of Object.entries(data)) {
        if (typeof resourceData === 'object' && resourceData !== null && 'id' in resourceData && 'data' in resourceData) {
          importedData[key] = resourceData as ImportedData;
        } else {
          errors.push(`Invalid data structure for ${key}`);
        }
      }
    }
    
    if (Object.keys(importedData).length === 0) {
      return {
        success: false,
        message: 'No valid data found in the JSON file',
        errors
      };
    }
    
    return {
      success: true,
      message: `Successfully imported ${Object.keys(importedData).length} data types`,
      importedData,
      errors: errors.length > 0 ? errors : undefined
    };
  } catch (error) {
    return {
      success: false,
      message: `Failed to process JSON file: ${error}`,
      errors: [error as string]
    };
  }
}

export async function importResourcesFromFile(file: File): Promise<ImportResult> {
  if (file.name.endsWith('.zip')) {
    return importResourcesFromZip(file);
  } else if (file.name.endsWith('.json')) {
    return importResourcesFromJson(file);
  } else {
    return {
      success: false,
      message: 'Unsupported file format. Please use .zip or .json files.',
      errors: ['Unsupported file format']
    };
  }
}

export function validateImportedData(importedData: { [key: string]: ImportedData }): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  const validTypes = ['raids', 'teams', 'toons', 'guilds', 'scenarios'];
  
  for (const [id, data] of Object.entries(importedData)) {
    if (!validTypes.includes(id)) {
      errors.push(`Unknown data type: ${id}`);
    }
    
    if (!Array.isArray(data.data)) {
      errors.push(`Data for ${id} is not an array`);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}
