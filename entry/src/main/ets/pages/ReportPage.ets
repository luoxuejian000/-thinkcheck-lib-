@Entry
@Component
struct ReportPage {
  build() {
    Column() {
      Text('历史对比').fontSize(24).margin(20)
      Text('对比多次诊断H值趋势，追踪推理质量变化（H值趋势反映了系统是否朝向更高谐振态演化）').fontSize(14).fontColor('#888888').padding(20)
    }
  }
}