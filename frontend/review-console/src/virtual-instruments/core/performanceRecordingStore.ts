import type { PerformanceRecording } from "./performanceRecorder";

const DATABASE_NAME = "music-education-virtual-instruments";
const DATABASE_VERSION = 1;
const STORE_NAME = "performances";

export class PerformanceRecordingStore {
  private databasePromise: Promise<IDBDatabase> | null = null;

  async save(recording: PerformanceRecording): Promise<void> {
    if (recording.durationMs > 300_000) throw new Error("Performance recording exceeds the five-minute limit");
    const database = await this.open();
    await requestToPromise(database.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME).put(recording));
  }

  async get(id: string): Promise<PerformanceRecording | null> {
    const database = await this.open();
    const value = await requestToPromise(database.transaction(STORE_NAME).objectStore(STORE_NAME).get(id));
    return (value as PerformanceRecording | undefined) ?? null;
  }

  async list(instrumentId?: string): Promise<PerformanceRecording[]> {
    const database = await this.open();
    const store = database.transaction(STORE_NAME).objectStore(STORE_NAME);
    const values = instrumentId
      ? await requestToPromise(store.index("instrumentId").getAll(instrumentId))
      : await requestToPromise(store.getAll());
    return (values as PerformanceRecording[]).sort((left, right) => right.createdAt.localeCompare(left.createdAt));
  }

  async delete(id: string): Promise<void> {
    const database = await this.open();
    await requestToPromise(database.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME).delete(id));
  }

  close(): void {
    void this.databasePromise?.then((database) => database.close());
    this.databasePromise = null;
  }

  private open(): Promise<IDBDatabase> {
    if (!globalThis.indexedDB) return Promise.reject(new Error("IndexedDB is unavailable on this device"));
    if (!this.databasePromise) {
      this.databasePromise = new Promise((resolve, reject) => {
        const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
        request.onupgradeneeded = () => {
          const database = request.result;
          const store = database.createObjectStore(STORE_NAME, { keyPath: "id" });
          store.createIndex("instrumentId", "instrumentId", { unique: false });
          store.createIndex("createdAt", "createdAt", { unique: false });
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error ?? new Error("Unable to open performance database"));
      });
    }
    return this.databasePromise;
  }
}

function requestToPromise<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB request failed"));
  });
}
