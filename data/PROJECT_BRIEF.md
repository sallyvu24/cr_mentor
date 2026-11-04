# Project brief: Tiền thuê nhà ở Sydney có phản ứng khác nhau quanh các khu campus không?

*Phiên bản cho business team. Trạng thái: phân tích khám phá đã chạy xong; chưa có mô hình dự báo và không nhằm đưa ra kết luận nhân quả.*

---

## 0. Tóm tắt trong một đoạn

Dự án dùng dữ liệu công khai của NSW để xem **giá thuê của các hợp đồng thuê mới ở Sydney có diễn biến khác nhau giữa khu gần các trường đại học và khu xa trường hay không**, và nếu có thì khác ở đâu, ở loại căn nào, lúc nào, và đáng tin đến mức nào. Người dùng chính là chuyên viên quy hoạch/nhà ở của **City of Sydney** (hội đồng thành phố), người cần một câu trả lời có thể bảo vệ được cho các cuộc thảo luận về nhà ở sinh viên. Kết quả hiện tại cho thấy **tín hiệu có nhưng chưa vững**: không đủ để chọn ra khu nào cần hành động riêng, nhưng đủ để chỉ ra nên xin thêm dữ liệu gì.

---

## 1. Dữ liệu được chọn gồm những gì?

### Nhóm dữ liệu chính (kết quả cần đo)

| Dữ liệu | Là gì | Quy mô | Vai trò |
|---|---|---|---|
| **Hợp đồng thuê mới (NSW Fair Trading, "rental bond")** | Mỗi dòng là một khoản tiền đặt cọc khi bắt đầu hợp đồng: ngày, postcode, loại nhà, số phòng ngủ, tiền thuê mỗi tuần | Khoảng 2.13 triệu dòng hợp lệ cho cả NSW; 1.48 triệu dòng thuộc 247 postcode của Sydney | **Thước đo chính:** giá thuê thực tế khi người thuê mới ký hợp đồng |
| Thời gian | Năm 2018 (trước COVID) và từ 01/2021 đến 09/2026 | | |

### Nhóm dữ liệu để biết "khu nào gần hoạt động giáo dục quốc tế"

| Dữ liệu | Là gì | Vai trò |
|---|---|---|
| **Danh bạ cơ sở đào tạo cho du học sinh (CRICOS)** | Danh sách trường, khóa học và địa điểm học | Xác định **vị trí campus**: 485 địa điểm đào tạo bậc đại học ở Greater Sydney, trong đó 16 campus lớn |
| **Số ghi danh du học sinh theo khu vực (Bộ Giáo dục)** | Số lượt ghi danh theo vùng thống kê, năm 2025 | Cho biết **vùng nào có nhiều sinh viên học**: riêng nội thành Sydney (City and Inner South) chiếm khoảng 6 trong 10 lượt ghi danh của Greater Sydney |
| **Visa sinh viên được cấp (Bộ Nội vụ)** | Số visa cấp theo tháng và theo bang | Xác định **các giai đoạn** sinh viên vào nhiều hay ít: đáy 11/2021, đỉnh 07/2023, và giảm dần đến 09/2026 |
| **Ranh giới postcode (ABS)** | Bản đồ và bảng quy đổi địa lý | Vẽ bản đồ và đo khoảng cách từ postcode đến campus |

### Nhóm dữ liệu bối cảnh (giúp tránh giải thích sai)

| Dữ liệu | Vai trò |
|---|---|
| **Hồ sơ xin phép xây dựng nhà ở (NSW Planning Portal)** | Xem nơi nào đang được **đề xuất** thêm nhà (4,326 hồ sơ trong 10 tháng mẫu) |
| **Tin đăng Airbnb (Inside Airbnb)** | Xem số căn cho thuê ngắn và trung hạn tại thời điểm 17/09/2026 (20,833 tin) |

### Dữ liệu đã cân nhắc nhưng không dùng

| Dữ liệu | Lý do |
|---|---|
| Giá bán nhà (Valuer General) | Trang bị chặn truy cập tự động; giấy phép không cho phép chia sẻ dữ liệu đã xử lý |
| Tin đăng thuê nhà thương mại (Domain, realestate.com.au) | Không có quyền truy cập dữ liệu đọc phù hợp; điều khoản chưa xác nhận |
| "Sức chứa đăng ký" của trường trong CRICOS | Tổng sức chứa lớn gấp hơn hai lần số ghi danh thực tế của cả NSW, nên không phản ánh nhu cầu |
| Dữ liệu thuê nhà của Victoria | Chỉ có số liệu tổng hợp theo quý, không có từng hợp đồng |

### Điều bộ dữ liệu **không** cho biết
Không có dữ liệu nào cho biết **ai** là người thuê (sinh viên hay không), và không có số sinh viên theo suburb. Vì vậy mức độ gắn với giáo dục quốc tế của từng khu được **suy ra** từ vị trí campus, không phải đo trực tiếp.

---

## 2. Người dùng, vấn đề kinh doanh và các cân nhắc nghiên cứu nền

### Người dùng
**Chuyên viên quy hoạch chiến lược / chính sách nhà ở của City of Sydney** (hỗ trợ nhóm Housing for All Working Group).

**Bằng chứng cho lựa chọn này (từ tài liệu gốc):**
- Ngày 20/02/2023, Hội đồng thành phố **nhất trí thông qua** một nghị quyết về tình trạng thiếu nhà ở sinh viên giá rẻ. Nghị quyết yêu cầu Giám đốc điều hành báo cáo các chiến lược xử lý áp lực nhà ở và chi phí sinh hoạt của sinh viên, và chuyển vấn đề sang nhóm Housing for All.
- Nghị quyết nêu: thành phố có khoảng 40% nhà cung cấp giáo dục của NSW; số phòng ở sinh viên tăng từ 4,223 (2012) lên 11,529 (2022); nhà ở sinh viên được báo là kín chỗ.
- Chính sách liên bang năm 2026 **gắn tăng chỉ tiêu tuyển sinh quốc tế của đại học công với việc cung cấp chỗ ở sinh viên**.

### Vấn đề kinh doanh
Hội đồng đang nói về nhà ở sinh viên dựa trên **số phòng và câu chuyện**, chưa có thước đo cho thấy **tiền thuê nhà mới ở khu gần campus có diễn biến khác với các khu tương tự nhưng xa campus hay không**. Họ cần biết:
1. Khu nào, loại căn nào, giai đoạn nào có dấu hiệu khác biệt.
2. Khác biệt đó lớn đến mức nào.
3. **Nên nói chắc đến mức nào** trong tài liệu báo cáo hoặc thư vận động.

### Những cân nhắc nghiên cứu đã làm để chọn đúng phạm vi

| Cân nhắc | Điều đã tìm ra | Ảnh hưởng đến thiết kế |
|---|---|---|
| **Ai có quyền quyết định?** | Chỉ tiêu du học sinh do chính phủ liên bang đặt; thành phố và bang có đòn bẩy về quy hoạch và nhà ở | Chọn người dùng ở cấp thành phố; không trả lời câu hỏi "cắt bao nhiêu sinh viên" |
| **Tình hình đã đổi chưa?** | Số du học sinh trên cả nước đã giảm (687,810 đến tháng 6/2026, giảm 7%); trần tuyển sinh đã tồn tại; nhập cư ròng từ sinh viên đã về mức trước COVID | Không coi "cắt thêm" là kịch bản mặc định; tập trung vào "ở đâu và chắc đến đâu" |
| **Ước tính sẵn có về tác động** | Các ước tính (RBA, Grattan, qua nguồn thứ cấp) cho rằng ảnh hưởng của sinh viên lên giá thuê là nhỏ | Thiết kế để phát hiện khác biệt nhỏ, và chấp nhận kết quả "chưa phân biệt được" |
| **Kiểm kê dữ liệu thật sự dùng được** | Từng nguồn được mở ra kiểm tra: có tải được không, mỗi dòng là gì, bao phủ thời gian nào, giấy phép ra sao | Chọn NSW vì chỉ NSW có giá thuê từng hợp đồng; loại các nguồn không dùng được |
| **Độ phủ và chất lượng** | 62 file hợp đồng thuê cùng một cấu trúc, không tháng nào thiếu từ 2021 đến 2026; ghép bảng CRICOS khớp 100%; file năm và file tháng khớp nhau; đã loại các dòng lỗi và ghi rõ số lượng | Có thể tin vào phạm vi dữ liệu; khoảng trống duy nhất là 2019-2020, đã được nêu rõ |
| **Đo cái gì cho công bằng?** | Khu gần campus vốn đắt hơn từ trước | So sánh **mức thay đổi**, không so mức giá; có năm 2018 làm mốc trước COVID |
| **Khu nào là đối chứng hợp lý?** | Nội thành toàn là căn hộ nhỏ, không so được với khu nhà riêng | Chỉ so với các khu **nhiều căn hộ** ở nơi khác; loại Central Coast vì là thị trường riêng |
| **Giai đoạn nào?** | Dòng visa sinh viên cho thấy 4 giai đoạn rõ rệt | Chia thời gian theo các giai đoạn này thay vì theo năm lịch |

---

## 3. Mục đích dự án và hướng phân tích

### Mục đích
Giúp người dùng **phân biệt tín hiệu thật với biến động chung của thị trường**, và cho biết bằng chứng hiện có đủ mạnh đến đâu trước khi dùng nó để ưu tiên khu vực hay viết kiến nghị. Đây là phân tích **khám phá**: tìm ra các hình mẫu và đo độ chắc chắn, không dự báo và không kết luận nguyên nhân.

### Bốn câu hỏi phân tích

| Câu hỏi | Nói đơn giản |
|---|---|
| **Chuyện gì đã xảy ra?** | Tiền thuê nhà mới thay đổi thế nào qua các giai đoạn, cho từng loại căn hộ? Có mô hình theo mùa gắn với năm học không? |
| **Ở đâu?** | Khu và hành lang nào tăng nhanh hoặc chậm hơn? |
| **Có liên hệ với campus không?** | Khu gần campus có tăng khác khu xa campus (cùng là khu nhiều căn hộ) không, và chênh lệch bao nhiêu? |
| **Khu nào cần xem tiếp?** | Hành lang nào nhất quán vượt mức tham chiếu và có đủ dữ liệu để tin? |

### Cách giữ cho kết luận trung thực
Mỗi mối liên hệ được xếp **hạng A, B hoặc C trước khi xem kết quả**:
- **A:** vững qua nhiều giai đoạn và nhiều cách đo; đáng được đào sâu.
- **B:** có tín hiệu nhưng phụ thuộc vào giai đoạn hoặc cách đo; chỉ nên nói là tạm thời.
- **C:** không phân biệt được với xu hướng chung.

Ngôn từ trong khuyến nghị tự đổi theo hạng này.

### Những gì đã thấy cho đến nay (sơ bộ, mức tin cậy B)
- **Một chu kỳ chung chi phối.** Tiền thuê căn hộ mới giảm 7-17% trong 2021 (biên giới đóng), rồi tăng khoảng 32-41% so với 2018 ở **mọi** nhóm khu vực. Khác biệt giữa các nhóm khi tính cả giai đoạn là nhỏ.
- **Dạng "giảm sâu hơn rồi hồi mạnh hơn".** Khu gần campus giảm nhiều hơn khoảng 10 điểm phần trăm trong 2021 và hồi mạnh hơn khoảng 9 điểm khi phục hồi. Tính cả giai đoạn từ 2018, khu gần campus tăng **ít hơn** khoảng 2.7 điểm. Kiểu biến động này cũng có thể do cú sốc chung của nội thành (văn phòng, du lịch), không riêng sinh viên.
- **Gợi ý về mùa vụ.** Ở khu gần campus, tiền thuê tháng 2 cao hơn xu hướng khoảng 4-5%, còn khu xa campus thì không. Dấu hiệu này nhất quán với lịch nhập học nhưng chỉ có 5 chu kỳ năm nên chưa đủ kết luận.
- **Không có hành lang gần campus nào luôn vượt khu tham chiếu.** Các hành lang luôn vượt đều là khu xa campus, nghĩa là tăng giá nhanh **không đặc trưng cho khu quanh trường**.

### Ý nghĩa với người dùng
Hiện chưa có cơ sở để xếp hạng các hành lang cho hành động liên quan đến sinh viên. Thay vào đó nên **xin thêm dữ liệu** để kiểm tra gợi ý mùa vụ (ngày bắt đầu hợp đồng và địa chỉ học kỳ do các đơn vị cung cấp nhà ở sinh viên nắm), đồng thời dùng phần mô tả (giá thuê đã phục hồi mạnh sau 2021 ở mọi khu) làm bối cảnh.

---

## 4. Các giới hạn đã nhận ra trong quá trình nghiên cứu và khám phá dữ liệu

### Về dữ liệu
1. **Không biết người thuê là ai.** Hợp đồng thuê không ghi sinh viên hay không; mức độ gắn với giáo dục quốc tế được suy ra từ vị trí campus.
2. **Số sinh viên theo vùng chỉ có một năm (2025)** và là nơi **học**, không phải nơi **ở**. Cách chia sinh viên về từng campus là một **giả định** (chia theo số khóa học), không phải số quan sát.
3. **Chỉ biết postcode**, và khoảng cách đo từ tâm postcode nên chính xác khoảng 1 km. Hai campus lớn (UNSW và Macquarie) có mã bưu chính riêng không nằm trong bản đồ nên được quy về postcode lân cận.
4. **Chỉ hợp đồng mới.** Dữ liệu không nói gì về tiền thuê của người đang thuê dài hạn.
5. **Thiếu 2019-2020** và dữ liệu 2018 lấy từ bản sao cổng dữ liệu NSW, cần xác nhận nguồn. Vì vậy chưa kiểm tra được liệu khu gần campus có xu hướng khác từ trước khi COVID xảy ra.
6. **Các giai đoạn dựa trên visa được cấp**, không phải số sinh viên thật sự có mặt; hai thước đo này lệch pha.
7. **Dữ liệu bối cảnh chưa đầy đủ:** hồ sơ xây dựng chỉ là đề xuất (nhiều hồ sơ không được xây) và mới lấy mẫu 10 tháng; Airbnb chỉ là một thời điểm.

### Về phân tích
8. **Đây là dữ liệu quan sát.** Các khu gần nhau chịu chung điều kiện, nên mối liên hệ không chứng minh nguyên nhân.
9. **Các cách đo mức gắn với campus đều xuất phát từ cùng một danh sách campus**, nên chúng đồng thuận cao. Điều này cho thấy kết quả không phụ thuộc vào chi tiết kỹ thuật, nhưng **không kiểm tra** giả định gốc rằng "gần campus nghĩa là sinh viên thuê ở đó".
10. **Hai điểm được thêm vào sau khi đã thấy kết quả đầu:** phần phân tích mùa vụ và quy tắc "hành lang phải thuộc nhóm gần campus". Vì vậy mùa vụ chỉ nên coi là gợi ý khám phá.
11. **Tín hiệu hạng B chủ yếu đến từ giai đoạn hồi phục sau 2021**, nên nhạy với việc cú sốc đó là của riêng sinh viên hay của cả nội thành.
12. **Người dùng chưa được xác nhận.** Bằng chứng về persona đến từ tài liệu công khai (và từ năm 2023); chưa có buổi trao đổi nào với người đang làm việc trong vai trò này.

### Cách làm chắc hơn trong bước tiếp theo
- Có thêm số **sinh viên theo suburb hoặc địa chỉ học kỳ** từ các trường hoặc đơn vị cung cấp nhà ở sinh viên.
- Có **dữ liệu 2019-2020** để kiểm tra xu hướng trước COVID.
- Dùng **số sinh viên có mặt theo tháng** thay cho dòng visa để xác định giai đoạn.
- Dữ liệu về **giá phòng và tỷ lệ lấp đầy** của nhà ở sinh viên chuyên dụng.
- Trao đổi với một người làm việc trong vai trò này để xác nhận nhu cầu thật.
