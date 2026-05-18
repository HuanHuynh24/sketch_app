export type Tier = "safe" | "balance" | "challenge";

export interface UniversityOption {
  id: string;
  tier: Tier;
  university: string;
  shortName: string;
  major: string;
  location: string;
  combo: string;
  predicted: number;
  ci: number;
  studentScore: number;
  gap: number;
  quota: number;
  competition: number;
  matchCode: string;
  matchPercent: number;
  trend: number[];
  traits: string[];
  tuition: string;
  scholarship: string;
}

export const options: UniversityOption[] = [
  {
    id: "spkt-cntt",
    tier: "safe",
    university: "Đại học Sư phạm Kỹ thuật - ĐH Đà Nẵng",
    shortName: "SPKT Đà Nẵng",
    major: "CNTT",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 25.5,
    ci: 0.6,
    studentScore: 26.1,
    gap: 0.6,
    quota: 120,
    competition: 13.2,
    matchCode: "RI",
    matchPercent: 89,
    trend: [22.8, 23.4, 24.2, 24.8, 25.1, 25.5],
    traits: ["Kỹ thuật", "Phân tích", "Lập trình", "Hệ thống"],
    tuition: "25 triệu / năm",
    scholarship: "Điểm ≥ 27.0 → 50% HV",
  },
  {
    id: "spkt-dien",
    tier: "safe",
    university: "Đại học Sư phạm Kỹ thuật - ĐH Đà Nẵng",
    shortName: "SPKT Đà Nẵng",
    major: "Kỹ thuật điện",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 22.3,
    ci: 0.7,
    studentScore: 26.1,
    gap: 3.8,
    quota: 90,
    competition: 8.4,
    matchCode: "RI",
    matchPercent: 84,
    trend: [20.1, 20.6, 21.4, 21.8, 22.0, 22.3],
    traits: ["Điện tử", "Thao tác", "Logic", "Thiết bị"],
    tuition: "24 triệu / năm",
    scholarship: "Top 10% đầu vào → 30% HV",
  },
  {
    id: "bkdn-cntt",
    tier: "balance",
    university: "Đại học Bách khoa - ĐH Đà Nẵng",
    shortName: "Bách khoa Đà Nẵng",
    major: "CNTT",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 28.1,
    ci: 0.5,
    studentScore: 26.1,
    gap: -2.0,
    quota: 180,
    competition: 18.6,
    matchCode: "RI",
    matchPercent: 92,
    trend: [26.1, 26.9, 27.2, 27.6, 27.9, 28.1],
    traits: ["Thuật toán", "Phân tích", "Hệ thống", "AI"],
    tuition: "29 triệu / năm",
    scholarship: "Điểm ≥ 28.5 → xét học bổng tài năng",
  },
  {
    id: "ued-is",
    tier: "balance",
    university: "Đại học Kinh tế - ĐH Đà Nẵng",
    shortName: "Kinh tế Đà Nẵng",
    major: "Hệ thống thông tin",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 25.8,
    ci: 0.6,
    studentScore: 26.1,
    gap: 0.3,
    quota: 130,
    competition: 11.8,
    matchCode: "IC",
    matchPercent: 78,
    trend: [23.8, 24.4, 24.9, 25.1, 25.5, 25.8],
    traits: ["Dữ liệu", "Quy trình", "Phân tích", "Sản phẩm"],
    tuition: "22 triệu / năm",
    scholarship: "GPA lớp 12 ≥ 8.8 → ưu tiên xét HB",
  },
  {
    id: "hust-cntt",
    tier: "challenge",
    university: "Đại học Bách khoa Hà Nội",
    shortName: "Bách khoa Hà Nội",
    major: "CNTT",
    location: "Hà Nội",
    combo: "A00",
    predicted: 29.2,
    ci: 0.4,
    studentScore: 26.1,
    gap: -3.1,
    quota: 300,
    competition: 24.9,
    matchCode: "RI",
    matchPercent: 94,
    trend: [28.0, 28.4, 28.8, 28.9, 29.0, 29.2],
    traits: ["Nghiên cứu", "Kỹ thuật", "AI", "Hệ thống lớn"],
    tuition: "35 triệu / năm",
    scholarship: "Theo đề án tài năng và hồ sơ học thuật",
  },
  {
    id: "bkdn-se",
    tier: "challenge",
    university: "Đại học Bách khoa - ĐH Đà Nẵng",
    shortName: "Bách khoa ĐN",
    major: "Kỹ thuật phần mềm",
    location: "Đà Nẵng",
    combo: "A00",
    predicted: 28.5,
    ci: 0.5,
    studentScore: 26.1,
    gap: -2.4,
    quota: 150,
    competition: 21.1,
    matchCode: "RI",
    matchPercent: 90,
    trend: [26.8, 27.2, 27.8, 28.0, 28.3, 28.5],
    traits: ["Lập trình", "Thiết kế hệ thống", "Kiểm thử", "Logic"],
    tuition: "31 triệu / năm",
    scholarship: "Điểm ≥ 28.0 → phỏng vấn học bổng",
  },
];
