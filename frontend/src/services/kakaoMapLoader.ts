const SDK_ID = "kakao-map-sdk";

export async function loadKakaoMaps(): Promise<NonNullable<Window["kakao"]>> {
  const appKey = import.meta.env.VITE_KAKAO_MAP_APP_KEY as string | undefined;
  if (!appKey || appKey.includes("YOUR_KAKAO_JS_KEY") || appKey.includes("****")) {
    throw new Error("VITE_KAKAO_MAP_APP_KEY가 설정되지 않았습니다.");
  }

  if (window.kakao?.maps) {
    return await new Promise((resolve) => window.kakao!.maps.load(() => resolve(window.kakao!)));
  }

  await new Promise<void>((resolve, reject) => {
    let script = document.getElementById(SDK_ID) as HTMLScriptElement | null;
    if (!script) {
      script = document.createElement("script");
      script.id = SDK_ID;
      script.async = true;
      script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${appKey}&autoload=false&libraries=services`;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("카카오맵 SDK 로드에 실패했습니다."));
      document.head.appendChild(script);
      return;
    }
    if (window.kakao?.maps) {
      resolve();
    } else {
      script.addEventListener("load", () => resolve(), { once: true });
      script.addEventListener("error", () => reject(new Error("카카오맵 SDK 로드에 실패했습니다.")), {
        once: true,
      });
    }
  });

  if (!window.kakao?.maps) {
    throw new Error("카카오맵 SDK가 초기화되지 않았습니다.");
  }
  return await new Promise((resolve) => window.kakao!.maps.load(() => resolve(window.kakao!)));
}
