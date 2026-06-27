package com.buyilehu.musicagent.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
                .authorizeRequests()
                .antMatchers("/api/v1/system/health", "/actuator/health", "/h2-console/**").permitAll()
                .anyRequest().authenticated()
                .and()
                .headers().frameOptions().sameOrigin()
                .and()
                .httpBasic();
        return http.build();
    }
}
