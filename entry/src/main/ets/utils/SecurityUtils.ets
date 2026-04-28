import { securityLabel } from '@ohos.securityLabel'

export class SecurityLabelManager {
  static async setDiagnosisSecurityLevel(filePath: string, domain: string): Promise<number> {
    let level: number
    switch (domain) {
      case 'medical': level = securityLabel.SecurityLevel.S4; break
      case 'legal':
      case 'financial': level = securityLabel.SecurityLevel.S3; break
      default: level = securityLabel.SecurityLevel.S2
    }
    await securityLabel.setSecurityLabel(filePath, level)
    return level
  }
}