import { useState } from "react";
import { verifyAdminSecret } from "../services/billboardsApi";

type Props = {
  adminMode: boolean;
  onAdminModeChange: (active: boolean, secret: string) => void;
};

export function AdminPanel({ adminMode, onAdminModeChange }: Props) {
  const [showInput, setShowInput] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);

  const handleLockClick = () => {
    if (adminMode) {
      onAdminModeChange(false, "");
      setPassword("");
      setShowInput(false);
    } else {
      setShowInput((prev) => !prev);
      setError(null);
    }
  };

  const handleConfirm = async () => {
    if (!password) return;
    setVerifying(true);
    setError(null);
    try {
      const ok = await verifyAdminSecret(password);
      if (ok) {
        sessionStorage.setItem("adminSecret", password);
        onAdminModeChange(true, password);
        setShowInput(false);
        setPassword("");
      } else {
        setError("비밀번호가 틀렸습니다.");
      }
    } catch {
      setError("인증 중 오류가 발생했습니다.");
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <button
        type="button"
        onClick={handleLockClick}
        title={adminMode ? "관리자 모드 해제" : "관리자 로그인"}
        style={{ fontSize: 18, background: "none", border: "none", cursor: "pointer" }}
      >
        {adminMode ? "🔓" : "🔒"}
      </button>
      {adminMode && <small style={{ color: "green" }}>관리자 모드</small>}
      {showInput && !adminMode && (
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <input
            type="password"
            placeholder="관리자 비밀번호"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") void handleConfirm(); }}
            style={{ padding: "2px 6px" }}
          />
          <button type="button" onClick={() => void handleConfirm()} disabled={verifying}>
            {verifying ? "확인 중..." : "확인"}
          </button>
          {error && <small style={{ color: "red" }}>{error}</small>}
        </span>
      )}
    </div>
  );
}
