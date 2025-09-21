# **3. UI 디자인 시스템 (UI Design System)**

**참조 문서**: [docs/0_architecture.md](docs/0_architecture.md), [docs/2_detailed_functional_specification.md](docs/2_detailed_functional_specification.md)

## **3.1 기본 디자인 토큰 (Design Tokens)**

### **3.1.1 색상 시스템**

#### **6가지 모자 색상 (Primary Colors)**
```css
/* 각 모자별 고유 브랜드 색상 */
--hat-white: #FFFFFF;      /* 하얀 모자 - 순수함, 객관성 */
--hat-red: #E53E3E;        /* 빨간 모자 - 열정, 감정 */
--hat-black: #2D3748;      /* 검은 모자 - 신중함, 비판 */
--hat-yellow: #F6E05E;     /* 노란 모자 - 밝음, 낙관 */
--hat-green: #38A169;      /* 초록 모자 - 창의성, 성장 */
--hat-blue: #3182CE;       /* 파란 모자 - 통제, 관리 */

/* 모자별 보조 색상 (각 색상의 다양한 톤) */
--hat-white-bg: #F7FAFC;
--hat-white-border: #E2E8F0;
--hat-red-light: #FEB2B2;
--hat-red-dark: #C53030;
--hat-black-light: #4A5568;
--hat-black-dark: #1A202C;
--hat-yellow-light: #F7DC6F;
--hat-yellow-dark: #D69E2E;
--hat-green-light: #68D391;
--hat-green-dark: #2F855A;
--hat-blue-light: #63B3ED;
--hat-blue-dark: #2B6CB0;
```

#### **시스템 색상 (System Colors)**
```css
/* 기본 UI 색상 */
--primary: #3182CE;        /* 메인 브랜드 색상 */
--secondary: #718096;      /* 보조 색상 */
--background: #FFFFFF;     /* 기본 배경 */
--surface: #F7FAFC;        /* 카드/컨테이너 배경 */
--border: #E2E8F0;         /* 기본 테두리 */
--text-primary: #2D3748;   /* 주요 텍스트 */
--text-secondary: #4A5568; /* 보조 텍스트 */
--text-muted: #718096;     /* 비활성 텍스트 */

/* 상태 색상 */
--success: #38A169;        /* 성공 */
--warning: #D69E2E;        /* 경고 */
--error: #E53E3E;          /* 오류 */
--info: #3182CE;           /* 정보 */

/* 코인 시스템 색상 */
--coin-gold: #FFD700;      /* 코인 색상 */
--coin-shadow: #DAA520;    /* 코인 그림자 */
```

### **3.1.2 타이포그래피**

#### **폰트 패밀리**
```css
/* 기본 폰트 */
--font-primary: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
--font-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;

/* 폰트 크기 */
--text-xs: 12px;     /* 보조 정보 */
--text-sm: 14px;     /* 일반 텍스트 */
--text-base: 16px;   /* 기본 텍스트 */
--text-lg: 18px;     /* 강조 텍스트 */
--text-xl: 20px;     /* 제목 */
--text-2xl: 24px;    /* 주요 제목 */
--text-3xl: 30px;    /* 화면 제목 */

/* 폰트 두께 */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* 행간 */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### **3.1.3 간격 시스템 (Spacing)**
```css
/* 8px 기반 간격 시스템 */
--space-1: 4px;      /* 최소 간격 */
--space-2: 8px;      /* 기본 단위 */
--space-3: 12px;     /* 작은 간격 */
--space-4: 16px;     /* 기본 간격 */
--space-5: 20px;     /* 중간 간격 */
--space-6: 24px;     /* 큰 간격 */
--space-8: 32px;     /* 섹션 간격 */
--space-10: 40px;    /* 화면 간격 */
--space-12: 48px;    /* 최대 간격 */

/* 특별 간격 */
--header-height: 60px;    /* 헤더 높이 */
--input-height: 48px;     /* 입력창 높이 */
--button-height: 44px;    /* 버튼 높이 */
--avatar-size: 40px;      /* 아바타 크기 */
```

### **3.1.4 그림자 및 테두리**
```css
/* 그림자 */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

/* 테두리 둥글기 */
--radius-sm: 4px;     /* 작은 둥글기 */
--radius-md: 8px;     /* 기본 둥글기 */
--radius-lg: 12px;    /* 큰 둥글기 */
--radius-xl: 16px;    /* 카드 둥글기 */
--radius-full: 9999px; /* 완전 둥글기 */

/* 테두리 두께 */
--border-thin: 1px;
--border-medium: 2px;
--border-thick: 3px;
```

## **3.2 UI 컴포넌트 라이브러리**

### **3.2.1 기본 컴포넌트**

#### **Button 컴포넌트**
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  children: ReactNode;
  onClick?: () => void;
}

// 스타일 정의
const buttonStyles = {
  base: {
    borderRadius: 'var(--radius-md)',
    fontWeight: 'var(--font-medium)',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--space-2)',
  },
  variants: {
    primary: {
      backgroundColor: 'var(--primary)',
      color: 'white',
      border: 'none',
    },
    secondary: {
      backgroundColor: 'var(--surface)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border)',
    },
    // ... 기타 variant들
  },
  sizes: {
    sm: { height: '32px', padding: '0 var(--space-3)', fontSize: 'var(--text-sm)' },
    md: { height: 'var(--button-height)', padding: '0 var(--space-4)', fontSize: 'var(--text-base)' },
    lg: { height: '52px', padding: '0 var(--space-6)', fontSize: 'var(--text-lg)' },
  }
};
```

#### **HatAvatar 컴포넌트**
```typescript
interface HatAvatarProps {
  hatType: 'white' | 'red' | 'black' | 'yellow' | 'green' | 'blue';
  isActive?: boolean;
  isTyping?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const hatAvatarStyles = {
  container: {
    width: 'var(--avatar-size)',
    height: 'var(--avatar-size)',
    borderRadius: 'var(--radius-full)',
    position: 'relative',
    transition: 'all 0.3s ease',
  },
  activeRing: {
    position: 'absolute',
    inset: '-4px',
    borderRadius: 'var(--radius-full)',
    background: 'linear-gradient(45deg, var(--primary), var(--secondary))',
    animation: 'pulse 2s infinite',
  },
  typingIndicator: {
    position: 'absolute',
    bottom: '-2px',
    right: '-2px',
    width: '12px',
    height: '12px',
    borderRadius: 'var(--radius-full)',
    backgroundColor: 'var(--success)',
    animation: 'bounce 1s infinite',
  }
};
```

#### **MessageBubble 컴포넌트**
```typescript
interface MessageBubbleProps {
  hatType: 'white' | 'red' | 'black' | 'yellow' | 'green' | 'blue';
  message: string;
  timestamp: Date;
  isStreaming?: boolean;
}

const messageBubbleStyles = {
  container: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 'var(--space-3)',
    padding: 'var(--space-4)',
    marginBottom: 'var(--space-3)',
  },
  bubble: {
    backgroundColor: 'var(--surface)',
    borderRadius: 'var(--radius-lg)',
    padding: 'var(--space-4)',
    boxShadow: 'var(--shadow-sm)',
    border: '1px solid var(--border)',
    maxWidth: '80%',
    position: 'relative',
  },
  // 각 모자별 테두리 색상
  hatBorders: {
    white: { borderLeftColor: 'var(--hat-white)', borderLeftWidth: '4px' },
    red: { borderLeftColor: 'var(--hat-red)', borderLeftWidth: '4px' },
    black: { borderLeftColor: 'var(--hat-black)', borderLeftWidth: '4px' },
    yellow: { borderLeftColor: 'var(--hat-yellow)', borderLeftWidth: '4px' },
    green: { borderLeftColor: 'var(--hat-green)', borderLeftWidth: '4px' },
    blue: { borderLeftColor: 'var(--hat-blue)', borderLeftWidth: '4px' },
  }
};
```

#### **InputField 컴포넌트**
```typescript
interface InputFieldProps {
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  maxLength?: number;
}

const inputFieldStyles = {
  container: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-2)',
  },
  input: {
    flex: 1,
    height: 'var(--input-height)',
    padding: '0 var(--space-4)',
    borderRadius: 'var(--radius-md)',
    border: '1px solid var(--border)',
    fontSize: 'var(--text-base)',
    backgroundColor: 'var(--background)',
    transition: 'border-color 0.2s',
  },
  inputFocus: {
    borderColor: 'var(--primary)',
    outline: 'none',
    boxShadow: '0 0 0 3px rgba(49, 130, 206, 0.1)',
  }
};
```

### **3.2.2 레이아웃 컴포넌트**

#### **ChatContainer 컴포넌트**
```typescript
interface ChatContainerProps {
  children: ReactNode;
  isLoading?: boolean;
}

const chatContainerStyles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: 'var(--background)',
  },
  header: {
    height: 'var(--header-height)',
    padding: '0 var(--space-4)',
    borderBottom: '1px solid var(--border)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'var(--surface)',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: 'var(--space-4)',
    display: 'flex',
    flexDirection: 'column',
  },
  inputArea: {
    padding: 'var(--space-4)',
    borderTop: '1px solid var(--border)',
    backgroundColor: 'var(--surface)',
  }
};
```

#### **CoinDisplay 컴포넌트**
```typescript
interface CoinDisplayProps {
  remainingCoins: number;
  totalCoins: number;
}

const coinDisplayStyles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    gap: 'var(--space-2)',
    padding: 'var(--space-2) var(--space-3)',
    backgroundColor: 'var(--coin-gold)',
    borderRadius: 'var(--radius-full)',
    boxShadow: 'var(--shadow-sm)',
  },
  icon: {
    width: '16px',
    height: '16px',
    color: 'var(--coin-shadow)',
  },
  text: {
    fontSize: 'var(--text-sm)',
    fontWeight: 'var(--font-semibold)',
    color: 'var(--coin-shadow)',
  }
};
```

## **3.3 화면별 레이아웃 설계**

### **3.3.1 메인 채팅 화면**
```
┌─────────────────────────────────────┐
│ 🎩 Six Sorting Hat    [5코인] ⚙️   │ ← Header
├─────────────────────────────────────┤
│ ⚪ 안녕하세요! 궁금한 것을          │
│    물어보세요.                      │
│                                     │
│ 🔴 사용자님의 감정을 이해해요.      │
│                                     │
│ ⚫ 위험 요소도 함께 고려해드려요.   │
│                                     │
│ 🟡 긍정적인 면도 놓치지 않아요!    │
│                                     │
│ 🟢 새로운 아이디어를 제안드려요.   │
│                                     │ ← Messages Area
│ 🔵 전체적으로 정리해드릴게요.      │
│                                     │
│ [ 현재 생각 중... ] ← 진행 상태     │
│                                     │
│                                     │
│                                     │
│                                     │
├─────────────────────────────────────┤
│ [무엇이든 물어보세요...        ] 📤│ ← Input Area
└─────────────────────────────────────┘
```

### **3.3.2 타이핑 상태 표시**
```
각 모자가 답변 중일 때의 시각적 표현:

⚪ [타이핑...] ← 현재 답변 중인 모자
🔴 [대기 중]  ← 다음 순서 모자들
⚫ [대기 중]
🟡 [대기 중]
🟢 [대기 중]
🔵 [대기 중]
```

## **3.4 반응형 및 접근성 고려사항**

### **3.4.1 반응형 브레이크포인트**
```css
/* 모바일 우선 설계 */
@media (min-width: 375px) {  /* Small phone */
  :root {
    --container-padding: var(--space-4);
    --message-max-width: 100%;
  }
}

@media (min-width: 768px) {  /* Tablet */
  :root {
    --container-padding: var(--space-6);
    --message-max-width: 80%;
  }
}

@media (min-width: 1024px) { /* Desktop */
  :root {
    --container-padding: var(--space-8);
    --message-max-width: 70%;
  }
}
```

### **3.4.2 접근성 (Accessibility)**
```css
/* 고대비 모드 지원 */
@media (prefers-contrast: high) {
  :root {
    --border: #000000;
    --text-primary: #000000;
    --background: #FFFFFF;
  }
}

/* 움직임 감소 모드 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 포커스 인디케이터 */
.focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

### **3.4.3 스크린 리더 지원**
```html
<!-- ARIA 라벨 예시 -->
<div role="log" aria-live="polite" aria-label="토론 진행 상황">
  <div role="article" aria-labelledby="white-hat">
    <h3 id="white-hat">하얀 모자의 답변</h3>
    <p>객관적인 정보를 분석하겠습니다...</p>
  </div>
</div>

<button aria-label="메시지 전송" aria-describedby="coin-count">
  <span id="coin-count">5개 코인 중 1개 사용</span>
</button>
```

## **3.5 애니메이션 및 트랜지션**

### **3.5.1 기본 애니메이션**
```css
/* 메시지 등장 애니메이션 */
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 타이핑 인디케이터 */
@keyframes typingDots {
  0%, 60%, 100% { opacity: 0.4; }
  30% { opacity: 1; }
}

/* 활성 모자 펄스 효과 */
@keyframes activePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(49, 130, 206, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(49, 130, 206, 0); }
}

/* 코인 반짝임 효과 */
@keyframes coinShine {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.2); }
}
```

### **3.5.2 상태 전환 애니메이션**
```css
/* 모자 전환 애니메이션 */
.hat-transition {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 메시지 버블 애니메이션 */
.message-bubble {
  animation: messageSlideIn 0.4s ease-out;
}

/* 로딩 상태 애니메이션 */
.loading-indicator {
  animation: typingDots 1.4s infinite ease-in-out;
}
```

## **3.6 구현 우선순위**

### **Phase 1 (MVP)**
1. **핵심 컴포넌트**:
   - HatAvatar (6가지 모자 아바타)
   - MessageBubble (메시지 버블)
   - InputField (질문 입력창)
   - Button (기본 버튼)
   - CoinDisplay (코인 표시)

2. **기본 화면**:
   - ChatContainer (메인 채팅 화면)
   - Header (앱 제목, 코인 표시)
   - MessageArea (토론 메시지 영역)
   - InputArea (질문 입력 영역)

3. **기본 색상**:
   - 6가지 모자 색상 시스템
   - 기본 UI 색상 (배경, 텍스트, 테두리)
   - 시스템 상태 색상

4. **기본 애니메이션**:
   - 메시지 등장 애니메이션
   - 타이핑 인디케이터
   - 버튼 호버 효과

### **Phase 2 (개선)**
1. **고급 컴포넌트**:
   - ProgressIndicator (진행 상황 표시)
   - ErrorBoundary (에러 처리 UI)
   - LoadingSpinner (로딩 표시)
   - Toast (알림 메시지)

2. **결과 화면**:
   - SummaryCard (토론 요약 카드)
   - HistoryList (토론 기록 목록)
   - ExportButton (결과 내보내기)

3. **접근성**:
   - 고대비 모드 지원
   - 스크린 리더 최적화
   - 키보드 네비게이션
   - 포커스 관리

4. **미세 애니메이션**:
   - 활성 모자 펄스 효과
   - 코인 사용 애니메이션
   - 스크롤 자동 이동
   - 상태 전환 효과

### **Phase 3 (고도화)**
1. **다크모드**:
   - 다크 테마 색상 시스템
   - 테마 전환 애니메이션
   - 시스템 설정 연동

2. **반응형**:
   - 태블릿 최적화
   - 데스크톱 지원
   - 가로/세로 모드 대응

3. **고급 애니메이션**:
   - 페이지 전환 효과
   - 제스처 기반 인터랙션
   - 물리 기반 애니메이션
   - 마이크로 인터랙션

## **3.7 성능 최적화 가이드**

### **3.7.1 렌더링 최적화**
- React.memo를 활용한 불필요한 리렌더링 방지
- 가상화를 통한 대량 메시지 목록 최적화
- 이미지 지연 로딩 및 최적화

### **3.7.2 애니메이션 최적화**
- CSS Transform과 Opacity만 사용하여 레이아웃 리플로우 방지
- will-change 속성 적절한 사용
- 60fps 유지를 위한 애니메이션 최적화

### **3.7.3 메모리 관리**
- 컴포넌트 언마운트 시 애니메이션 정리
- 이벤트 리스너 적절한 해제
- 큰 객체 참조 방지
