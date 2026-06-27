package com.buyilehu.musicagent;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class MusicAgentServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(MusicAgentServerApplication.class, args);
    }
}
