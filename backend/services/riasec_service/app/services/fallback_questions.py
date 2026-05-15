GENERIC_FALLBACK_QUESTIONS = [
    (
        "Gian hàng hướng nghiệp của lớp sắp mở cửa nhưng mọi thứ còn khá rối: poster chưa xong, thông tin ngành còn thiếu, "
        "bàn trải nghiệm chưa thử và nhóm chưa phân công rõ. Nếu em chỉ kịp nhận một phần quan trọng nhất, em sẽ làm gì trước và vì sao?"
    ),
    (
        "Nhóm em có 2 ngày để làm một video ngắn giới thiệu ngành học cho học sinh lớp 10. Ý tưởng còn mơ hồ, dữ liệu chưa chắc, "
        "và người thuyết trình hơi lo. Em muốn chen vào xử lý phần nào để video tốt hơn? Vì sao?"
    ),
    (
        "CLB của em chuẩn bị workshop nhưng số người đăng ký ít hơn dự kiến. Có bạn đề xuất đổi nội dung, có bạn muốn gọi thêm người, "
        "có bạn muốn chỉnh lại kế hoạch vận hành. Nếu là em, em sẽ chọn hướng xử lý nào trước? Vì sao?"
    ),
    (
        "Hãy nhớ một hoạt động gần đây ở trường khiến em thấy mình có ích nhất. Khi đó em thiên về tự tay làm, phân tích vấn đề, "
        "nghĩ ý tưởng, hỗ trợ người khác, dẫn dắt nhóm hay sắp xếp công việc? Em đã làm gì cụ thể?"
    ),
]


FOCUSED_FALLBACK_QUESTIONS = {
    ("R", "I"): [
        (
            "Mô hình demo trong buổi trải nghiệm STEM chạy không ổn ngay trước giờ trình bày. Em muốn mở ra kiểm tra từng phần và thử lại, "
            "hay xem dữ liệu/lỗi ghi nhận để tìm nguyên nhân trước? Vì sao cách đó hợp với em hơn?"
        ),
        (
            "Nhóm em cần chứng minh một ý tưởng kỹ thuật có dùng được không. Em thích bắt tay làm mẫu thử để quan sát kết quả, "
            "hay phân tích nguyên lý và số liệu trước khi làm? Hãy nói rõ cách em sẽ bắt đầu."
        ),
    ],
    ("I", "A"): [
        (
            "Video giới thiệu ngành của lớp đang bị nhận xét là vừa thiếu thông tin vừa chưa cuốn. Em muốn đào sâu dữ liệu để làm nội dung chắc hơn, "
            "hay đổi cách kể chuyện/hình ảnh để người xem thấy hứng thú hơn? Vì sao?"
        ),
        (
            "Một ứng dụng học tập trong dự án của nhóm bị chê khó dùng. Em muốn phân tích hành vi người dùng để tìm vấn đề gốc, "
            "hay phác lại trải nghiệm và giao diện cho dễ hiểu hơn? Em sẽ làm bước nào trước?"
        ),
    ],
    ("S", "E"): [
        (
            "Trong buổi chuẩn bị sự kiện, một bạn trong nhóm bị rối và tiến độ chung bắt đầu chậm. Em muốn ngồi kèm bạn ấy để gỡ từng phần, "
            "hay đứng ra phân công lại và kéo cả nhóm về đúng hạn? Vì sao?"
        ),
        (
            "Gian hàng của CLB vắng người ghé qua. Em muốn ra trò chuyện để hiểu và hỗ trợ từng bạn tham gia, "
            "hay chủ động kêu gọi, giới thiệu và tạo không khí để kéo nhiều người hơn? Vì sao?"
        ),
    ],
    ("E", "C"): [
        (
            "Buổi tư vấn chọn ngành còn 30 phút nữa bắt đầu, nhưng danh sách khách mời và timeline đều chưa chắc. Em muốn đứng ra điều phối mọi người, "
            "hay lập checklist thật nhanh để kiểm soát từng việc? Vì sao?"
        ),
        (
            "Kế hoạch tham quan doanh nghiệp của lớp cần được duyệt gấp. Em muốn thuyết phục giáo viên và các bạn đồng ý phương án, "
            "hay rà lại chi phí, lịch trình, phân công để không sót lỗi? Em sẽ ưu tiên gì trước?"
        ),
    ],
}


def select_fallback_question(
    focus_groups: list[str],
    history_text: str,
) -> str:
    pair = tuple(sorted(focus_groups[:2]))
    candidates = FOCUSED_FALLBACK_QUESTIONS.get(pair, []) + GENERIC_FALLBACK_QUESTIONS

    for candidate in candidates:
        if candidate.lower() not in history_text:
            return candidate

    return GENERIC_FALLBACK_QUESTIONS[len(history_text) % len(GENERIC_FALLBACK_QUESTIONS)]
