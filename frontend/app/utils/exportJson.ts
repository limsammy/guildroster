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