export const syncFuncWithMessages = async (messages: string[], iterateFunc: (x: any, i: number) => void) => {
  for (let i = 0; i < messages.length; i++) {
    const message = messages[i];
    const delay = Math.max(message.length * 100, 2000); // Calculate delay based on string length, max 2 seconds
    iterateFunc(message, i);
    await new Promise((resolve) => setTimeout(resolve, delay));
  }
};