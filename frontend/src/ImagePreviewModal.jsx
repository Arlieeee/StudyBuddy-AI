import { useEffect, useCallback } from 'react'

/**
 * 图像预览Modal组件
 * 功能：全屏预览图像，支持下载和关闭
 */
function ImagePreviewModal({ imageBase64, onClose }) {
    // ESC键关闭
    const handleKeyDown = useCallback((e) => {
        if (e.key === 'Escape') {
            onClose()
        }
    }, [onClose])

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown)
        // 禁止背景滚动
        document.body.style.overflow = 'hidden'

        return () => {
            document.removeEventListener('keydown', handleKeyDown)
            document.body.style.overflow = 'auto'
        }
    }, [handleKeyDown])

    // 下载图像
    const handleDownload = () => {
        const link = document.createElement('a')
        link.href = `data:image/png;base64,${imageBase64}`
        link.download = `知识图解_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    // 点击背景关闭
    const handleBackdropClick = (e) => {
        if (e.target.className === 'image-modal-backdrop') {
            onClose()
        }
    }

    return (
        <div className="image-modal-backdrop" onClick={handleBackdropClick}>
            <div className="image-modal-container">
                {/* 右上角工具栏 */}
                <div className="image-modal-toolbar">
                    <button
                        className="image-modal-btn"
                        onClick={handleDownload}
                        title="下载图像"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="7 10 12 15 17 10" />
                            <line x1="12" y1="15" x2="12" y2="3" />
                        </svg>
                    </button>
                    <button
                        className="image-modal-btn image-modal-close"
                        onClick={onClose}
                        title="关闭 (ESC)"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                {/* 图像内容 */}
                <div className="image-modal-content">
                    <img
                        src={`data:image/png;base64,${imageBase64}`}
                        alt="知识图解预览"
                        className="image-modal-img"
                    />
                </div>
            </div>
        </div>
    )
}

export default ImagePreviewModal
