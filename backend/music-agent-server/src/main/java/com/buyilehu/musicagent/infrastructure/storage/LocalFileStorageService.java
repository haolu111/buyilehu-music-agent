package com.buyilehu.musicagent.infrastructure.storage;

import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.config.FileStorageProperties;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Service
public class LocalFileStorageService implements FileStorageService {
    private final Path root;

    public LocalFileStorageService(FileStorageProperties properties) {
        this.root = properties.getRoot().toAbsolutePath().normalize();
    }

    @Override
    public String store(String directory, String filename, InputStream content) {
        String safeFilename = UUID.randomUUID() + extensionOf(filename);
        Path target = root.resolve(directory).resolve(safeFilename).normalize();
        if (!target.startsWith(root)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "非法存储路径");
        }
        try {
            Files.createDirectories(target.getParent());
            Files.copy(content, target, StandardCopyOption.REPLACE_EXISTING);
            return root.relativize(target).toString().replace('\\', '/');
        } catch (IOException exception) {
            throw new BusinessException(ErrorCode.INTERNAL_ERROR, "文件保存失败");
        }
    }

    @Override
    public Path resolve(String relativePath) {
        Path target = root.resolve(relativePath).normalize();
        if (!target.startsWith(root)) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "非法文件路径");
        }
        return target;
    }

    private String extensionOf(String filename) {
        int index = filename == null ? -1 : filename.lastIndexOf('.');
        return index < 0 ? "" : filename.substring(index).toLowerCase();
    }
}
