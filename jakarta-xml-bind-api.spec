Name:		jakarta-xml-bind-api
Version:	4.0.2
Release:	1
Summary:	Jakarta XML Binding API
Group:		Development/Java
License:	BSD-3-Clause
URL:		https://github.com/jakartaee/jaxb-api
# Tag 4.0.2. Gradle 9.9.1 accepts this coordinate.
Source0:	https://github.com/jakartaee/jaxb-api/archive/refs/tags/%{version}.tar.gz#/jakarta-xml-bind-api-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(jakarta.activation:jakarta.activation-api)

%description
Jakarta XML Binding API 4.0.2. Gradle 9.9.1 accepts this
coordinate. The implementation is a separate package.

%prep
%autosetup -n jaxb-api-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
mkdir -p classes
find api/src/main/java -name '*.java' ! -name module-info.java > sources.list
test "$(wc -l < sources.list)" -eq 96
javac --release 11 -encoding UTF-8 -Xlint:-options \
	-cp "%{_javadir}/jakarta.activation-api.jar" \
	-d classes @sources.list
/bin/cp -a api/src/main/resources/. classes/
jar cf jakarta.xml.bind-api.jar -C classes .
cat > jakarta.xml.bind-api.pom <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>jakarta.xml.bind</groupId>
  <artifactId>jakarta.xml.bind-api</artifactId>
  <version>4.0.2</version>
  <name>Jakarta XML Binding API</name>
  <description>Jakarta XML Binding API 4.0.</description>
  <url>https://github.com/jakartaee/jaxb-api</url>
  <licenses>
    <license>
      <name>BSD-3-Clause</name>
      <url>https://www.eclipse.org/org/documents/edl-v10.php</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>jakarta.activation</groupId>
      <artifactId>jakarta.activation-api</artifactId>
      <version>2.1.3</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact jakarta.xml.bind-api.pom:jakarta.xml.bind-api.jar \
	--file-name jakarta.xml.bind-api \
	--filelist .mfiles

%check
JAR=%{buildroot}%{_javadir}/jakarta.xml.bind-api.jar
test -f "$JAR"
mkdir -p check
cat > check/Smoke.java <<'END'
import jakarta.xml.bind.JAXBElement;
import javax.xml.namespace.QName;
public class Smoke {
	public static void main(String[] args) {
		JAXBElement<String> el = new JAXBElement<>(
			new QName("urn:test", "a"), String.class, "xmlbind_ok");
		System.out.println(el.getName().getNamespaceURI() + " " + el.getValue());
	}
}
END
javac --release 11 -encoding UTF-8 -Xlint:-options \
	-cp "$JAR:%{_javadir}/jakarta.activation-api.jar" \
	-d check check/Smoke.java
java -cp "check:$JAR:%{_javadir}/jakarta.activation-api.jar" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'urn:test xmlbind_ok' check/out.txt

%files -f .mfiles
%license LICENSE.md
%doc README.md NOTICE.md
