package com.buyilehu.musicagent.infrastructure.repository;

import com.buyilehu.musicagent.domain.entity.LessonPlan;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface LessonPlanRepository extends JpaRepository<LessonPlan, Long> {
    List<LessonPlan> findByTeacherIdOrderByIdDesc(Long teacherId);
}
