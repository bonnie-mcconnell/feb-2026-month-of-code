import { open } from "fs/promises";

const SAMPLE_SIZE = 8000;
const NULL_BYTE_THRESHOLD = 0.01;
const NON_PRINTABLE_THRESHOLD = 0.3;

export async function isBinaryFile(filePath: string): Promise<boolean> {
  const file = await open(filePath, "r");

  try {
    const buffer = Buffer.alloc(SAMPLE_SIZE);
    const { bytesRead } = await file.read(buffer, 0, SAMPLE_SIZE, 0);

    if (bytesRead === 0) return false;

    let nullBytes = 0;
    let nonPrintable = 0;

    for (let i = 0; i < bytesRead; i++) {
      const byte = buffer[i];

      if (byte === 0) nullBytes++;

      if (
        byte < 7 ||
        (byte > 14 && byte < 32) ||
        byte > 127
      ) {
        nonPrintable++;
      }
    }

    const nullRatio = nullBytes / bytesRead;
    const nonPrintableRatio = nonPrintable / bytesRead;

    return (
      nullRatio > NULL_BYTE_THRESHOLD ||
      nonPrintableRatio > NON_PRINTABLE_THRESHOLD
    );
  } finally {
    await file.close();
  }
}
