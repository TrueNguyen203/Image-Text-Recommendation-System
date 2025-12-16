export default function Footer() {
    return (
        <div className="min-h-80 bottom-0 h-40 bg-[#444343] flex items-center justify-between xl:px-32 md:px-16 sm: px-8 py-4 gap-8">
            <div className="flex flex-col">
                <h2 className="text-white text-3xl">Contributors</h2>
                <a href="https://github.com/TrueNguyen203" className="text-white text-lg"> - Chu Cao Nguyên</a>
                <a href="https://github.com/DucAnhShyyy" className="text-white text-lg"> - Nguyễn Đức Anh</a>
                <a href="https://github.com/thanh2004" className="text-white text-lg"> - Nguyễn Tiến Tuấn Thành</a>
                <a href="https://github.com/Thedungx723" className="text-white text-lg"> - Nguyễn Mạnh Dũng</a>
                <a href="https://github.com/ToanNguyn" className="text-white text-lg"> - Nguyễn Khánh Toàn</a>
            </div>
            <div>
                <h2 className="text-white text-3xl">
                    <a href="https://github.com/TrueNguyen203/Image-Text-Recommendation-System/tree/merging_csv" className="text-3xl">The code source located here!</a>
                </h2>
            </div>
        </div>
    )
}