"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.statusLabels = void 0;
exports.statusText = statusText;
exports.formatDateTime = formatDateTime;
exports.statusLabels = {
    active: '使用中', inactive: '已停用', uploaded: '已上传', processing: '解析中',
    success: '解析成功', failed: '解析失败', pending: '等待处理', draft: '草稿',
    confirmed: '已确认', generated: '已生成', modified: '已修改', published: '已发布', not_started: '待开始',
    running: '进行中', paused: '已暂停', ended: '已结束', locked: '未开启', unlocked: '已开启',
};
function statusText(value) {
    if (!value)
        return '未知状态';
    return exports.statusLabels[value] || value;
}
function formatDateTime(value) {
    if (!value)
        return '时间待定';
    var date = new Date(value);
    if (Number.isNaN(date.getTime()))
        return value.replace('T', ' ').slice(0, 16);
    return new Intl.DateTimeFormat('zh-CN', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(date);
}
