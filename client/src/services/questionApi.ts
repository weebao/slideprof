export const ask = async (question: string, imageCoords: any) => {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question, imageCoords }),
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