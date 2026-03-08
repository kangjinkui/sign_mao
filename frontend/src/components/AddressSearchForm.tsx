import { FormEvent, useState } from "react";

type Props = {
  onSearch: (address: string) => void;
  loading: boolean;
};

export function AddressSearchForm({ onSearch, loading }: Props) {
  const [address, setAddress] = useState("");

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (address.trim().length < 2) return;
    onSearch(address.trim());
  };

  return (
    <form onSubmit={onSubmit} style={{ display: "flex", gap: 8 }}>
      <input
        aria-label="address-input"
        value={address}
        onChange={(event) => setAddress(event.target.value)}
        placeholder="주소를 입력하세요"
        style={{ flex: 1, padding: 8 }}
      />
      <button type="submit" disabled={loading}>
        {loading ? "검색중" : "검색"}
      </button>
    </form>
  );
}
