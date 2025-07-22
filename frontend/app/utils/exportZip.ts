import JSZip from 'jszip';

export async function exportResourcesAsZip(resources: { [filename: string]: () => Promise<any> }, selected: string[], zipName = 'guildroster-export.zip') {
  const zip = new JSZip();

  // Fetch and add each selected resource as a JSON file
  await Promise.all(selected.map(async (key) => {
    if (resources[key]) {
      const data = await resources[key]();
      zip.file(`${key}.json`, JSON.stringify(data, null, 2));
    }
  }));

  // Generate the zip and trigger download
  const blob = await zip.generateAsync({ type: 'blob' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = zipName;
  a.click();
  URL.revokeObjectURL(url);
} 