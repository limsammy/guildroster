/**
 * Utility function to export data as JSON and trigger a download
 * @param data - The data to export
 * @param filename - The filename for the downloaded file
 */
export function exportJson(data: any, filename: string) {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();

  URL.revokeObjectURL(url);
}

/**
 * Export all resources as a single JSON blob for easy copy-pasting
 * @param resources - Object containing resource fetchers
 * @param selected - Array of selected resource keys
 * @param filename - The filename for the downloaded file
 */
export async function exportAllAsJson(
  resources: { [filename: string]: () => Promise<any> }, 
  selected: string[], 
  filename = 'guildroster-export.json'
) {
  const exportData: { [key: string]: any } = {};
  
  // Fetch all selected resources
  await Promise.all(selected.map(async (key) => {
    if (resources[key]) {
      const data = await resources[key]();
      exportData[key] = {
        id: key,
        exported_at: new Date().toISOString(),
        data: data
      };
    }
  }));

  // Export as a single JSON file
  exportJson(exportData, filename);
}

/**
 * Copy all resources as a single JSON string to clipboard
 * @param resources - Object containing resource fetchers
 * @param selected - Array of selected resource keys
 */
export async function copyAllAsJson(
  resources: { [filename: string]: () => Promise<any> }, 
  selected: string[]
): Promise<string> {
  const exportData: { [key: string]: any } = {};
  
  // Fetch all selected resources
  await Promise.all(selected.map(async (key) => {
    if (resources[key]) {
      const data = await resources[key]();
      exportData[key] = {
        id: key,
        exported_at: new Date().toISOString(),
        data: data
      };
    }
  }));

  const jsonString = JSON.stringify(exportData, null, 2);
  
  // Copy to clipboard
  try {
    await navigator.clipboard.writeText(jsonString);
    return jsonString;
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    // Fallback: return the string so user can manually copy
    return jsonString;
  }
} 