import * as admin from 'firebase-admin';
import fs from 'fs';
import path from 'path';

let db: any;
let isMockDb = false;

try {
  if (!admin.apps.length) {
    admin.initializeApp({
      credential: admin.credential.applicationDefault()
    });
  }
  db = admin.firestore();
  // Validate if firestore is truly reachable (throws if projectId is missing)
  if (!process.env.GOOGLE_APPLICATION_CREDENTIALS && !process.env.FIREBASE_CONFIG && !process.env.GCLOUD_PROJECT) {
    throw new Error("Missing Google Cloud environment project credentials.");
  }
} catch (error) {
  console.warn('⚠️ Firebase Admin failed to initialize. Activating high-fidelity local JSON database fallback:', error);
  isMockDb = true;

  const getLocalPath = (filename: string) => {
    // Relative to parent backend workspace
    const baseDir = path.join(process.cwd(), '..', 'backend');
    if (!fs.existsSync(baseDir)) {
      fs.mkdirSync(baseDir, { recursive: true });
    }
    return path.join(baseDir, filename);
  };

  // Mock Firestore implementation with high compatibility
  db = {
    collection: (colName: string) => {
      const filePath = getLocalPath(`${colName}.json`);
      
      const readData = () => {
        if (!fs.existsSync(filePath)) return [];
        try {
          return JSON.parse(fs.readFileSync(filePath, 'utf8'));
        } catch {
          return [];
        }
      };

      const writeData = (data: any) => {
        try {
          fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
        } catch (e) {
          console.error("Local DB write error:", e);
        }
      };

      return {
        doc: (docId: string) => {
          return {
            get: async () => {
              const data = readData();
              const found = data.find((item: any) => item.id === docId);
              return {
                exists: !!found,
                data: () => found ? found.data : null
              };
            },
            set: async (docData: any) => {
              const data = readData();
              const idx = data.findIndex((item: any) => item.id === docId);
              if (idx > -1) {
                data[idx].data = docData;
              } else {
                data.push({ id: docId, data: docData });
              }
              writeData(data);
              return { success: true };
            },
            update: async (docData: any) => {
              const data = readData();
              const idx = data.findIndex((item: any) => item.id === docId);
              if (idx > -1) {
                data[idx].data = { ...data[idx].data, ...docData };
              } else {
                data.push({ id: docId, data: docData });
              }
              writeData(data);
              return { success: true };
            }
          };
        },
        add: async (docData: any) => {
          const data = readData();
          const newDoc = { id: Math.random().toString(36).substr(2, 9), data: docData };
          data.push(newDoc);
          writeData(data);
          return { id: newDoc.id };
        }
      };
    },
    runTransaction: async (updateFunction: (transaction: any) => Promise<any>) => {
      const transactionMock = {
        get: async (docRef: any) => {
          return await docRef.get();
        },
        set: async (docRef: any, data: any) => {
          return await docRef.set(data);
        },
        update: async (docRef: any, data: any) => {
          return await docRef.update(data);
        }
      };
      return await updateFunction(transactionMock);
    }
  };
}

export { db, isMockDb };
