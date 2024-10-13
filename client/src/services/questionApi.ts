export const ask = async (filename: string, pageNumber: number, question: string, imageCoords: any) => {
  try {
    console.log(question, imageCoords, filename, pageNumber);
  
    const res = await fetch(`${process.env.API_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filename, pageNumber, question, imageCoords }),
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    return data;
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
}