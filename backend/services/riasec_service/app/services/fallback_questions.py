RIASEC_ORDER = ["R", "I", "A", "S", "E", "C"]


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


FOCUSED_FALLBACK_QUESTIONS.update(
    {
        ("R", "A"): [
            (
                "Bàn trải nghiệm cần vừa chắc chắn vừa thu hút người xem. Em muốn tự tay chỉnh mô hình/sản phẩm để chạy ổn hơn, "
                "hay thiết kế lại phần hình ảnh và cách kể chuyện để gian hàng nổi bật hơn? Em sẽ bắt đầu thế nào?"
            ),
            (
                "Nhóm có một vật mẫu cho buổi giới thiệu ngành nhưng nhìn còn khô. Em nghiêng về việc cải tiến vật mẫu để người xem chạm thử được, "
                "hay làm poster/video sáng tạo để giải thích ý tưởng? Vì sao?"
            ),
        ],
        ("R", "S"): [
            (
                "Trong buổi trải nghiệm, một bạn mới không biết dùng bộ dụng cụ và bắt đầu nản. Em muốn trực tiếp thao tác mẫu cho bạn quan sát, "
                "hay ngồi hướng dẫn từng bước để bạn tự làm được? Vì sao cách đó hợp với em?"
            ),
            (
                "Nhóm cần chuẩn bị khu thực hành cho khách tham gia. Em thích kiểm tra dụng cụ, setup bàn trải nghiệm, "
                "hay đứng hỗ trợ từng bạn tham gia hiểu cách làm? Em sẽ ưu tiên việc nào trước?"
            ),
        ],
        ("R", "E"): [
            (
                "Gian hàng STEM thiếu người phụ trách ngay trước giờ mở cửa. Em muốn vào xử lý thiết bị để phần demo chạy ổn, "
                "hay đứng ra mời người tham gia và điều phối nhóm để gian hàng đông hơn? Vì sao?"
            ),
            (
                "Sản phẩm demo có lỗi nhỏ nhưng nhóm cũng cần người thuyết phục ban giám khảo. Em sẽ ưu tiên sửa lỗi kỹ thuật, "
                "hay nhận vai trò trình bày và kéo sự chú ý về điểm mạnh của sản phẩm? Nói rõ lý do."
            ),
        ],
        ("R", "C"): [
            (
                "Trước giờ demo, dụng cụ đặt lộn xộn và checklist an toàn chưa xong. Em muốn tự tay sắp lại thiết bị, thử từng phần, "
                "hay lập danh sách kiểm tra để cả nhóm làm đúng quy trình? Vì sao?"
            ),
            (
                "Nhóm cần hoàn thiện mô hình và hồ sơ nộp kèm. Em nghiêng về việc chỉnh mô hình cho chắc, "
                "hay rà soát thông số, minh chứng và biểu mẫu để không sai sót? Em sẽ bắt đầu từ đâu?"
            ),
        ],
        ("I", "S"): [
            (
                "Kết quả khảo sát chọn ngành của lớp có nhiều câu trả lời mâu thuẫn, trong khi vài bạn đang bối rối. Em muốn phân tích dữ liệu để tìm xu hướng thật, "
                "hay trao đổi với từng bạn để hiểu nhu cầu và hỗ trợ họ? Vì sao?"
            ),
            (
                "Một bạn hỏi nên chọn ngành nào nhưng thông tin bạn ấy đưa ra còn ít. Em sẽ đặt câu hỏi và phân tích dữ kiện trước, "
                "hay lắng nghe, trấn an rồi giúp bạn diễn đạt mong muốn rõ hơn? Nói rõ cách em làm."
            ),
        ],
        ("I", "E"): [
            (
                "Nhóm cần chọn ý tưởng dự thi trong 20 phút. Em muốn kiểm chứng dữ liệu và rủi ro của từng ý tưởng, "
                "hay nhanh chóng thuyết phục cả nhóm chọn một hướng có cơ hội thắng cao? Vì sao?"
            ),
            (
                "Một đề xuất nghe rất hấp dẫn nhưng số liệu chưa chắc. Em sẽ đào sâu bằng chứng trước khi quyết, "
                "hay đứng ra bán ý tưởng và tìm người ủng hộ để kịp deadline? Em nghiêng về cách nào?"
            ),
        ],
        ("I", "C"): [
            (
                "Bảng khảo sát nghề nghiệp có dữ liệu lệch và file tổng hợp chưa sạch. Em muốn tìm nguyên nhân bằng cách phân tích mẫu trả lời, "
                "hay chuẩn hóa bảng, đặt quy tắc nhập liệu và kiểm tra lỗi? Vì sao?"
            ),
            (
                "Nhóm cần nộp báo cáo khảo sát trong chiều nay. Em sẽ ưu tiên rút insight từ dữ liệu, "
                "hay rà soát format, nguồn, bảng biểu và thứ tự nội dung để báo cáo chặt chẽ? Nói rõ lý do."
            ),
        ],
        ("A", "S"): [
            (
                "Video truyền thông của lớp cần vừa cảm xúc vừa giúp bạn xem thấy được quan tâm. Em muốn viết lại câu chuyện/hình ảnh cho cuốn hơn, "
                "hay phỏng vấn và hỗ trợ các bạn chia sẻ trải nghiệm thật? Vì sao?"
            ),
            (
                "CLB muốn làm một hoạt động cho học sinh mới. Em nghiêng về tạo concept, poster và nội dung hấp dẫn, "
                "hay thiết kế hoạt động để các bạn dễ kết nối và được hỗ trợ? Em sẽ làm gì trước?"
            ),
        ],
        ("A", "E"): [
            (
                "Chiến dịch tuyển thành viên cần ý tưởng mới và cũng cần người kéo tương tác. Em muốn tạo concept/hình ảnh thật khác biệt, "
                "hay đứng ra pitching, kêu gọi và làm không khí sôi nổi hơn? Vì sao?"
            ),
            (
                "Một gian hàng ít người ghé dù phần trang trí chưa xong. Em sẽ đổi cách trình bày nội dung cho bắt mắt, "
                "hay chủ động mời gọi, giới thiệu và thuyết phục người xem tham gia? Nói rõ lựa chọn."
            ),
        ],
        ("A", "C"): [
            (
                "Poster sự kiện có ý tưởng hay nhưng thông tin ngày giờ, địa điểm, phân công còn rối. Em muốn chỉnh concept và hình ảnh cho đẹp hơn, "
                "hay rà soát bố cục, thông tin và checklist để không sai chi tiết? Vì sao?"
            ),
            (
                "Nhóm làm video giới thiệu ngành nhưng deadline sát. Em sẽ ưu tiên phần kịch bản/hình ảnh sáng tạo, "
                "hay dựng timeline, đặt tên file, kiểm tra phụ đề và thứ tự cảnh cho đúng? Em nghiêng về đâu?"
            ),
        ],
        ("S", "C"): [
            (
                "Buổi tư vấn có nhiều phụ huynh hỏi cùng lúc, còn danh sách câu hỏi chưa được sắp xếp. Em muốn trực tiếp lắng nghe và hỗ trợ từng người, "
                "hay phân loại câu hỏi, lập thứ tự xử lý và ghi chép rõ ràng? Vì sao?"
            ),
            (
                "Một bạn trong nhóm làm chậm vì không hiểu nhiệm vụ, còn deadline đang đến gần. Em sẽ ngồi kèm bạn ấy, "
                "hay chia nhỏ việc, lập checklist và theo dõi tiến độ để bạn làm đúng? Nói rõ cách em chọn."
            ),
        ],
    }
)


def select_fallback_question(
    focus_groups: list[str],
    history_text: str,
) -> str:
    pair = tuple(
        sorted(
            focus_groups[:2],
            key=lambda group: RIASEC_ORDER.index(group)
            if group in RIASEC_ORDER
            else len(RIASEC_ORDER),
        )
    )
    candidates = FOCUSED_FALLBACK_QUESTIONS.get(pair, []) + GENERIC_FALLBACK_QUESTIONS

    for candidate in candidates:
        if candidate.lower() not in history_text:
            return candidate

    return GENERIC_FALLBACK_QUESTIONS[len(history_text) % len(GENERIC_FALLBACK_QUESTIONS)]
