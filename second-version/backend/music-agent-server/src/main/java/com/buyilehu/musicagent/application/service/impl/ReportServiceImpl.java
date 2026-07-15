package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.response.ClassroomReportResponse;
import com.buyilehu.musicagent.application.dto.response.ClassroomReportResponse.NodeCompletionReport;
import com.buyilehu.musicagent.application.dto.response.ClassroomReportResponse.StudentCompletionReport;
import com.buyilehu.musicagent.application.service.ReportService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ActivityNode;
import com.buyilehu.musicagent.domain.entity.ClassMember;
import com.buyilehu.musicagent.domain.entity.ClassroomSession;
import com.buyilehu.musicagent.domain.entity.LearningEvent;
import com.buyilehu.musicagent.domain.entity.StudentProgress;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.repository.ActivityNodeRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassMemberRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassroomSessionRepository;
import com.buyilehu.musicagent.infrastructure.repository.LearningEventRepository;
import com.buyilehu.musicagent.infrastructure.repository.StudentProgressRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ReportServiceImpl implements ReportService {
    private final ClassroomSessionRepository classroomSessionRepository;
    private final ClassMemberRepository classMemberRepository;
    private final StudentProgressRepository studentProgressRepository;
    private final LearningEventRepository learningEventRepository;
    private final ActivityNodeRepository activityNodeRepository;
    private final UserRepository userRepository;

    public ReportServiceImpl(ClassroomSessionRepository classroomSessionRepository,
                             ClassMemberRepository classMemberRepository,
                             StudentProgressRepository studentProgressRepository,
                             LearningEventRepository learningEventRepository,
                             ActivityNodeRepository activityNodeRepository,
                             UserRepository userRepository) {
        this.classroomSessionRepository = classroomSessionRepository;
        this.classMemberRepository = classMemberRepository;
        this.studentProgressRepository = studentProgressRepository;
        this.learningEventRepository = learningEventRepository;
        this.activityNodeRepository = activityNodeRepository;
        this.userRepository = userRepository;
    }

    @Override
    @Transactional(readOnly = true)
    public ClassroomReportResponse getClassroomSessionReport(Long sessionId) {
        User teacher = getCurrentTeacher();
        ClassroomSession session = classroomSessionRepository.findByIdAndTeacherId(sessionId, teacher.getId())
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "session not found"));

        List<ClassMember> members = classMemberRepository.findByClassIdAndStatusOrderByIdAsc(session.getClassId(), "active");
        List<Long> studentIds = new ArrayList<>();
        for (ClassMember member : members) {
            if ("student".equals(member.getRole())) {
                studentIds.add(member.getUserId());
            }
        }

        List<ActivityNode> nodes = activityNodeRepository.findByPackageIdOrderBySortOrderAsc(session.getPackageId());
        List<StudentProgress> progresses = studentProgressRepository.findBySessionId(sessionId);
        List<LearningEvent> events = learningEventRepository.findBySessionIdOrderByOccurredAtDesc(sessionId);

        Set<Long> enteredStudentIds = collectEnteredStudentIds(events);
        Map<Long, User> usersById = findUsersById(studentIds);
        Map<Long, List<StudentProgress>> progressByStudent = groupProgressByStudent(progresses);
        Map<Long, Set<Long>> completedNodesByStudent = groupCompletedNodesByStudent(progresses);

        ClassroomReportResponse response = new ClassroomReportResponse();
        response.setSessionId(session.getId());
        response.setClassId(session.getClassId());
        response.setPackageId(session.getPackageId());
        response.setTotalStudentCount(studentIds.size());
        response.setEnteredStudentCount(countKnownStudents(enteredStudentIds, studentIds));
        response.setCompletedStudentCount(countStudentsCompletedAllNodes(studentIds, completedNodesByStudent, nodes.size()));
        response.setAverageScore(round(averageScore(progresses)));
        response.setAverageDurationSeconds(round(averageDuration(progresses)));
        response.setNodeReports(buildNodeReports(nodes, progresses, studentIds.size()));
        response.setStudentReports(buildStudentReports(studentIds, usersById, enteredStudentIds, progressByStudent, completedNodesByStudent));
        return response;
    }

    private Set<Long> collectEnteredStudentIds(List<LearningEvent> events) {
        Set<Long> enteredStudentIds = new HashSet<>();
        for (LearningEvent event : events) {
            if (event.getStudentId() != null && "node_enter".equals(event.getEventType())) {
                enteredStudentIds.add(event.getStudentId());
            }
        }
        return enteredStudentIds;
    }

    private Map<Long, User> findUsersById(List<Long> studentIds) {
        Map<Long, User> usersById = new HashMap<>();
        for (User user : userRepository.findAllById(studentIds)) {
            usersById.put(user.getId(), user);
        }
        return usersById;
    }

    private Map<Long, List<StudentProgress>> groupProgressByStudent(List<StudentProgress> progresses) {
        Map<Long, List<StudentProgress>> result = new HashMap<>();
        for (StudentProgress progress : progresses) {
            if (!result.containsKey(progress.getStudentId())) {
                result.put(progress.getStudentId(), new ArrayList<StudentProgress>());
            }
            result.get(progress.getStudentId()).add(progress);
        }
        return result;
    }

    private Map<Long, Set<Long>> groupCompletedNodesByStudent(List<StudentProgress> progresses) {
        Map<Long, Set<Long>> result = new HashMap<>();
        for (StudentProgress progress : progresses) {
            if (!"completed".equals(progress.getProgressStatus()) || progress.getCurrentNodeId() == null) {
                continue;
            }
            if (!result.containsKey(progress.getStudentId())) {
                result.put(progress.getStudentId(), new HashSet<Long>());
            }
            result.get(progress.getStudentId()).add(progress.getCurrentNodeId());
        }
        return result;
    }

    private int countKnownStudents(Set<Long> ids, List<Long> knownStudentIds) {
        int count = 0;
        for (Long studentId : knownStudentIds) {
            if (ids.contains(studentId)) {
                count++;
            }
        }
        return count;
    }

    private int countStudentsCompletedAllNodes(List<Long> studentIds, Map<Long, Set<Long>> completedNodesByStudent, int nodeCount) {
        if (nodeCount <= 0) {
            return 0;
        }
        int count = 0;
        for (Long studentId : studentIds) {
            Set<Long> completedNodes = completedNodesByStudent.get(studentId);
            if (completedNodes != null && completedNodes.size() >= nodeCount) {
                count++;
            }
        }
        return count;
    }

    private List<NodeCompletionReport> buildNodeReports(List<ActivityNode> nodes, List<StudentProgress> progresses, int totalStudents) {
        List<NodeCompletionReport> reports = new ArrayList<>();
        for (ActivityNode node : nodes) {
            Set<Long> completedStudents = new HashSet<>();
            for (StudentProgress progress : progresses) {
                if (node.getId().equals(progress.getCurrentNodeId()) && "completed".equals(progress.getProgressStatus())) {
                    completedStudents.add(progress.getStudentId());
                }
            }
            NodeCompletionReport report = new NodeCompletionReport();
            report.setNodeId(node.getId());
            report.setTitle(node.getTitle());
            report.setNodeType(node.getNodeType());
            report.setSortOrder(node.getSortOrder());
            report.setCompletedCount(completedStudents.size());
            report.setCompletionRate(totalStudents == 0 ? 0.0 : round((completedStudents.size() * 1.0) / totalStudents));
            reports.add(report);
        }
        return reports;
    }

    private List<StudentCompletionReport> buildStudentReports(List<Long> studentIds,
                                                              Map<Long, User> usersById,
                                                              Set<Long> enteredStudentIds,
                                                              Map<Long, List<StudentProgress>> progressByStudent,
                                                              Map<Long, Set<Long>> completedNodesByStudent) {
        List<StudentCompletionReport> reports = new ArrayList<>();
        for (Long studentId : studentIds) {
            List<StudentProgress> progresses = progressByStudent.get(studentId);
            if (progresses == null) {
                progresses = new ArrayList<>();
            }
            Set<Long> completedNodeIds = completedNodesByStudent.get(studentId);
            if (completedNodeIds == null) {
                completedNodeIds = new HashSet<>();
            }

            StudentCompletionReport report = new StudentCompletionReport();
            report.setStudentId(studentId);
            User user = usersById.get(studentId);
            report.setStudentName(user == null ? "" : user.getRealName());
            report.setEntered(enteredStudentIds.contains(studentId));
            report.setCompletedNodeCount(completedNodeIds.size());
            report.setCompletedNodeIds(new ArrayList<Long>(completedNodeIds));
            report.setWrongCount(sumWrongCount(progresses));
            report.setHintUsedCount(sumHintUsedCount(progresses));
            report.setTotalDurationSeconds(sumDuration(progresses));
            report.setTotalScore(sumScore(progresses));
            report.setAverageScore(round(averageScore(progresses)));
            reports.add(report);
        }
        return reports;
    }

    private double averageScore(List<StudentProgress> progresses) {
        int count = 0;
        int total = 0;
        for (StudentProgress progress : progresses) {
            if ("completed".equals(progress.getProgressStatus()) && progress.getScore() != null) {
                total += progress.getScore();
                count++;
            }
        }
        return count == 0 ? 0.0 : total * 1.0 / count;
    }

    private double averageDuration(List<StudentProgress> progresses) {
        int count = 0;
        int total = 0;
        for (StudentProgress progress : progresses) {
            if ("completed".equals(progress.getProgressStatus()) && progress.getDurationSeconds() != null) {
                total += progress.getDurationSeconds();
                count++;
            }
        }
        return count == 0 ? 0.0 : total * 1.0 / count;
    }

    private int sumWrongCount(List<StudentProgress> progresses) {
        int total = 0;
        for (StudentProgress progress : progresses) {
            total += progress.getWrongCount() == null ? 0 : progress.getWrongCount();
        }
        return total;
    }

    private int sumHintUsedCount(List<StudentProgress> progresses) {
        int total = 0;
        for (StudentProgress progress : progresses) {
            total += progress.getHintUsedCount() == null ? 0 : progress.getHintUsedCount();
        }
        return total;
    }

    private int sumDuration(List<StudentProgress> progresses) {
        int total = 0;
        for (StudentProgress progress : progresses) {
            total += progress.getDurationSeconds() == null ? 0 : progress.getDurationSeconds();
        }
        return total;
    }

    private int sumScore(List<StudentProgress> progresses) {
        int total = 0;
        for (StudentProgress progress : progresses) {
            total += progress.getScore() == null ? 0 : progress.getScore();
        }
        return total;
    }

    private Double round(double value) {
        return Math.round(value * 100.0) / 100.0;
    }

    private User getCurrentTeacher() {
        User user = userRepository.findById(getCurrentUserId())
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "login user not found"));
        if (user.getRole() != UserRole.teacher) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "teacher permission required");
        }
        return user;
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "login required");
    }
}