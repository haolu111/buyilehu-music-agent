package com.buyilehu.musicagent.application.service.impl;

import com.buyilehu.musicagent.application.dto.request.CreateClassRequest;
import com.buyilehu.musicagent.application.dto.request.JoinClassRequest;
import com.buyilehu.musicagent.application.dto.response.ClassResponse;
import com.buyilehu.musicagent.application.dto.response.ClassStudentResponse;
import com.buyilehu.musicagent.application.service.ClassService;
import com.buyilehu.musicagent.common.exception.BusinessException;
import com.buyilehu.musicagent.common.exception.ErrorCode;
import com.buyilehu.musicagent.domain.entity.ClassEntity;
import com.buyilehu.musicagent.domain.entity.ClassMember;
import com.buyilehu.musicagent.domain.entity.User;
import com.buyilehu.musicagent.domain.entity.UserRole;
import com.buyilehu.musicagent.infrastructure.repository.ClassMemberRepository;
import com.buyilehu.musicagent.infrastructure.repository.ClassRepository;
import com.buyilehu.musicagent.infrastructure.repository.UserRepository;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ClassServiceImpl implements ClassService {
    private static final String ACTIVE = "active";
    private static final String STUDENT_MEMBER_ROLE = "student";
    private static final String INVITE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    private static final SecureRandom RANDOM = new SecureRandom();

    private final ClassRepository classRepository;
    private final ClassMemberRepository classMemberRepository;
    private final UserRepository userRepository;

    public ClassServiceImpl(ClassRepository classRepository,
                            ClassMemberRepository classMemberRepository,
                            UserRepository userRepository) {
        this.classRepository = classRepository;
        this.classMemberRepository = classMemberRepository;
        this.userRepository = userRepository;
    }

    @Override
    @Transactional
    public ClassResponse create(CreateClassRequest request) {
        User currentUser = getCurrentUser();
        ensureRole(currentUser, UserRole.teacher, "只有教师可以创建班级");

        ClassEntity classEntity = new ClassEntity();
        classEntity.setClassName(request.getClassName());
        classEntity.setDescription(request.getDescription());
        classEntity.setTeacherId(currentUser.getId());
        classEntity.setInviteCode(generateInviteCode());
        classEntity.setStatus(ACTIVE);

        return ClassResponse.from(classRepository.save(classEntity));
    }

    @Override
    @Transactional(readOnly = true)
    public List<ClassResponse> listMine() {
        User currentUser = getCurrentUser();
        if (currentUser.getRole() == UserRole.teacher) {
            return classRepository.findByTeacherIdOrderByIdDesc(currentUser.getId())
                    .stream()
                    .map(ClassResponse::from)
                    .collect(Collectors.toList());
        }

        List<Long> classIds = classMemberRepository.findByUserIdAndStatusOrderByIdDesc(currentUser.getId(), ACTIVE)
                .stream()
                .map(ClassMember::getClassId)
                .collect(Collectors.toList());

        return classRepository.findAllById(classIds)
                .stream()
                .map(ClassResponse::from)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public ClassResponse join(JoinClassRequest request) {
        User currentUser = getCurrentUser();
        ensureRole(currentUser, UserRole.student, "只有学生可以加入班级");

        String inviteCode = request.getInviteCode().trim().toUpperCase(Locale.ROOT);
        ClassEntity classEntity = classRepository.findByInviteCode(inviteCode)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "班级邀请码不存在"));

        if (!ACTIVE.equals(classEntity.getStatus())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "班级不可加入");
        }
        if (classMemberRepository.existsByClassIdAndUserId(classEntity.getId(), currentUser.getId())) {
            throw new BusinessException(ErrorCode.BAD_REQUEST, "你已加入该班级");
        }

        ClassMember member = new ClassMember();
        member.setClassId(classEntity.getId());
        member.setUserId(currentUser.getId());
        member.setRole(STUDENT_MEMBER_ROLE);
        member.setStatus(ACTIVE);
        classMemberRepository.save(member);

        return ClassResponse.from(classEntity);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ClassStudentResponse> listStudents(Long classId) {
        User currentUser = getCurrentUser();
        ensureRole(currentUser, UserRole.teacher, "只有教师可以查看班级学生");

        ClassEntity classEntity = classRepository.findById(classId)
                .orElseThrow(() -> new BusinessException(ErrorCode.RESOURCE_NOT_FOUND, "班级不存在"));
        if (!currentUser.getId().equals(classEntity.getTeacherId())) {
            throw new BusinessException(ErrorCode.FORBIDDEN, "只能查看自己班级的学生");
        }

        List<ClassStudentResponse> students = new ArrayList<>();
        List<ClassMember> members = classMemberRepository.findByClassIdAndStatusOrderByIdAsc(classId, ACTIVE);
        for (ClassMember member : members) {
            userRepository.findById(member.getUserId())
                    .ifPresent(user -> students.add(ClassStudentResponse.from(member, user)));
        }
        return students;
    }

    private User getCurrentUser() {
        Long currentUserId = getCurrentUserId();
        return userRepository.findById(currentUserId)
                .orElseThrow(() -> new BusinessException(ErrorCode.UNAUTHORIZED, "登录用户不存在"));
    }

    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
        }
        Object principal = authentication.getPrincipal();
        if (principal instanceof Long) {
            return (Long) principal;
        }
        if (principal instanceof String) {
            return Long.valueOf((String) principal);
        }
        throw new BusinessException(ErrorCode.UNAUTHORIZED, "未登录或登录已失效");
    }

    private void ensureRole(User user, UserRole requiredRole, String message) {
        if (user.getRole() != requiredRole) {
            throw new BusinessException(ErrorCode.FORBIDDEN, message);
        }
    }

    private String generateInviteCode() {
        for (int attempt = 0; attempt < 10; attempt++) {
            String code = randomInviteCode();
            if (!classRepository.existsByInviteCode(code)) {
                return code;
            }
        }
        throw new BusinessException(ErrorCode.INTERNAL_ERROR, "生成班级邀请码失败");
    }

    private String randomInviteCode() {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < 8; i++) {
            builder.append(INVITE_CHARS.charAt(RANDOM.nextInt(INVITE_CHARS.length())));
        }
        return builder.toString();
    }
}
