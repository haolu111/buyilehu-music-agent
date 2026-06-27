package com.buyilehu.musicagent.infrastructure.storage;

import java.io.InputStream;
import java.nio.file.Path;

public interface FileStorageService {
    String store(String directory, String filename, InputStream content);
    Path resolve(String relativePath);
}
