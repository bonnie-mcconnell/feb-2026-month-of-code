export interface ScannerConfig {
  rootPath: string;
  entropyThreshold: number;
  minEntropyLength: number;
  customIgnorePath?: string;
}

export const DEFAULT_CONFIG: Omit<ScannerConfig, "rootPath"> = {
  entropyThreshold: 4.5,
  minEntropyLength: 20
};
