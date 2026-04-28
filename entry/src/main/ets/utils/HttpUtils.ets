import { http } from '@kit.NetworkKit';

import { DiagnosisRequest, DiagnosisResult } from '../common/Constants';

export class RestDiagnosisService {

  private static readonly BASE_URL = 'https://api.thinkcheck.cn/v4'

  static async diagnose(request: DiagnosisRequest): Promise<DiagnosisResult> {
    const httpRequest = http.createHttp()
    const response = await httpRequest.request(
      `${RestDiagnosisService.BASE_URL}/diagnose`,
      {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify(request),
        connectTimeout: 30000, readTimeout: 60000
      }
    )
    if (response.responseCode !== 200) throw new Error(`服务器错误: ${response.responseCode}`)
    return JSON.parse(response.result as string) as DiagnosisResult
  }
}